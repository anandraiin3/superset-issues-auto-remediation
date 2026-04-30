"""Remediation orchestrator — manages Devin session lifecycle.

RO-01 – RO-11: Creates sessions via Devin API, polls until terminal
state, extracts PR URL, and handles timeouts / failures.
"""

import time
from typing import Optional

import requests

from src.config import Config
from src.database import (
    create_session,
    session_exists_for_issue,
    update_session_status,
)
from src.logger import get_logger
from src.prompt_builder import build_prompt

logger = get_logger(__name__)

DEVIN_API_BASE = "https://api.devin.ai"

TERMINAL_STATUSES = {"finished", "expired"}
ACTIVE_STATUSES = {"working", "blocked", "resumed"}


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {Config.DEVIN_API_KEY}",
        "Content-Type": "application/json",
    }


def _create_devin_session(
    prompt: str,
    issue_number: int,
    issue_title: str,
) -> dict:
    """Call Devin API to create a new session (RO-03 / RO-04)."""
    payload = {
        "prompt": prompt,
        "idempotent": True,
        "title": f"Remediate #{issue_number}: {issue_title}",
        "tags": ["auto-remediation", f"issue-{issue_number}"],
    }

    resp = requests.post(
        f"{DEVIN_API_BASE}/v1/sessions",
        json=payload,
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _poll_session(session_id: str) -> dict:
    """Retrieve current session details from Devin API (RO-05)."""
    resp = requests.get(
        f"{DEVIN_API_BASE}/v1/sessions/{session_id}",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _extract_pr_url(session_data: dict) -> Optional[str]:
    """Extract PR URL from session response (RO-06)."""
    pr_info = session_data.get("pull_request")
    if pr_info and isinstance(pr_info, dict):
        return pr_info.get("url")
    return None


def remediate_issue(
    repo_url: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
) -> None:
    """End-to-end remediation: create session, poll, extract result.

    This function runs in a background thread — it must not raise
    unhandled exceptions.
    """
    log_extra = {"issue_number": issue_number}

    try:
        # RO-01: Idempotency check
        if session_exists_for_issue(issue_number):
            logger.info(
                f"Session already exists for issue #{issue_number} — skipping",
                extra={**log_extra, "event_type": "idempotency_skip"},
            )
            return

        # Build prompt (PR-01 – PR-04)
        prompt = build_prompt(repo_url, issue_number, issue_title, issue_body)

        # RO-03 / RO-04: Create Devin session
        logger.info(
            f"Creating Devin session for issue #{issue_number}",
            extra={**log_extra, "event_type": "session_creating"},
        )
        result = _create_devin_session(prompt, issue_number, issue_title)
        session_id = result["session_id"]
        log_extra["session_id"] = session_id

        # Persist to DB
        create_session(session_id, issue_number, issue_title, repo_url)
        update_session_status(session_id, "running")

        logger.info(
            f"Devin session created: {session_id} — url: {result.get('url', 'N/A')}",
            extra={**log_extra, "event_type": "session_started"},
        )

        # RO-05: Poll until terminal state
        timeout_seconds = Config.SESSION_TIMEOUT_MINUTES * 60
        start = time.monotonic()

        while True:
            elapsed = time.monotonic() - start

            # RO-08: Timeout guard
            if elapsed > timeout_seconds:
                logger.warning(
                    f"Session {session_id} timed out after {Config.SESSION_TIMEOUT_MINUTES}m",
                    extra={**log_extra, "event_type": "session_timed_out"},
                )
                update_session_status(
                    session_id,
                    "timed_out",
                    error_message=f"Session exceeded {Config.SESSION_TIMEOUT_MINUTES} minute timeout",
                    error_type="timeout",
                )
                return

            time.sleep(Config.POLLING_INTERVAL_SECONDS)

            try:
                session_data = _poll_session(session_id)
            except requests.RequestException as exc:
                logger.warning(
                    f"Poll request failed for {session_id}: {exc}",
                    extra={**log_extra, "event_type": "poll_error"},
                )
                continue

            status_enum = session_data.get("status_enum", "")
            logger.info(
                f"Session {session_id} status: {status_enum}",
                extra={**log_extra, "event_type": "poll_status"},
            )

            if status_enum == "finished":
                pr_url = _extract_pr_url(session_data)
                update_session_status(session_id, "completed", pr_url=pr_url)
                logger.info(
                    f"Session {session_id} completed — PR: {pr_url or 'none'}",
                    extra={**log_extra, "event_type": "session_completed"},
                )
                return

            if status_enum in ("expired",):
                update_session_status(
                    session_id,
                    "failed",
                    error_message=f"Devin session reached terminal status: {status_enum}",
                    error_type="devin_terminal",
                )
                logger.warning(
                    f"Session {session_id} ended with status: {status_enum}",
                    extra={**log_extra, "event_type": "session_failed"},
                )
                return

            if status_enum not in ACTIVE_STATUSES:
                logger.info(
                    f"Session {session_id} in non-active status: {status_enum}",
                    extra={**log_extra, "event_type": "poll_status_unknown"},
                )

    except requests.HTTPError as exc:
        logger.error(
            f"Devin API error for issue #{issue_number}: {exc}",
            extra={**log_extra, "event_type": "api_error"},
            exc_info=True,
        )
        if "session_id" in log_extra:
            update_session_status(
                log_extra["session_id"],
                "failed",
                error_message=str(exc),
                error_type="api_error",
            )
    except Exception as exc:
        logger.error(
            f"Unexpected error remediating issue #{issue_number}: {exc}",
            extra={**log_extra, "event_type": "unexpected_error"},
            exc_info=True,
        )
        if "session_id" in log_extra:
            update_session_status(
                log_extra["session_id"],
                "failed",
                error_message=str(exc),
                error_type="unexpected",
            )
