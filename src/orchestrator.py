"""Remediation orchestrator — manages Devin session lifecycle.

RO-01 – RO-11: Creates sessions via Devin API **v3**, polls until terminal
state, extracts PR URL, and handles timeouts / failures.  Supports
all GitHub issue types (bug, feature, task).

API reference: https://docs.devin.ai/api-reference/overview
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

# v3 terminal statuses — the session will not transition further.
# "exit" = completed (check status_detail for "finished"),
# "error" = unrecoverable error,
# "suspended" = paused (inactivity, user request, usage limit, etc.)
TERMINAL_STATUSES = {"exit", "error", "suspended"}

# v3 running sub-states (status_detail when status == "running")
ACTIVE_DETAILS = {"working", "waiting_for_user", "waiting_for_approval"}


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {Config.DEVIN_API_KEY}",
        "Content-Type": "application/json",
    }


def _sessions_url() -> str:
    """Build the v3 sessions endpoint URL for the configured organisation."""
    return f"{DEVIN_API_BASE}/v3/organizations/{Config.DEVIN_ORG_ID}/sessions"


def _create_devin_session(
    prompt: str,
    issue_number: int,
    issue_title: str,
    issue_type: str = "task",
) -> dict:
    """Call Devin API v3 to create a new session (RO-03 / RO-04).

    v3 endpoint: POST /v3/organizations/{org_id}/sessions
    Idempotency is handled at the application level (DB check in
    remediate_issue) since v3 does not expose an idempotent flag.
    """
    payload: dict = {
        "prompt": prompt,
        "title": f"Resolve #{issue_number} [{issue_type}]: {issue_title}",
        "tags": ["auto-remediation", f"issue-{issue_number}", issue_type],
    }

    resp = requests.post(
        _sessions_url(),
        json=payload,
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _poll_session(session_id: str) -> dict:
    """Retrieve current session details from Devin API v3 (RO-05).

    v3 endpoint: GET /v3/organizations/{org_id}/sessions/{session_id}
    """
    resp = requests.get(
        f"{_sessions_url()}/{session_id}",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _extract_pr_url(session_data: dict) -> Optional[str]:
    """Extract the first PR URL from session response (RO-06).

    v3 returns ``pull_requests``: a list of ``{pr_url, pr_state}`` objects
    (changed from v1's single ``pull_request.url``).
    """
    prs = session_data.get("pull_requests")
    if prs and isinstance(prs, list):
        for pr in prs:
            url = pr.get("pr_url")
            if url:
                return url
    return None


def remediate_issue(
    repo_url: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
    issue_type: str = "task",
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
        prompt = build_prompt(
            repo_url, issue_number, issue_title, issue_body, issue_type
        )

        # RO-03 / RO-04: Create Devin session (v3)
        logger.info(
            f"Creating Devin session for issue #{issue_number} (type={issue_type})",
            extra={**log_extra, "event_type": "session_creating"},
        )
        result = _create_devin_session(prompt, issue_number, issue_title, issue_type)
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

            status = session_data.get("status", "")
            status_detail = session_data.get("status_detail", "")
            logger.info(
                f"Session {session_id} status: {status} (detail: {status_detail})",
                extra={**log_extra, "event_type": "poll_status"},
            )

            # v3: "exit" with status_detail "finished" means task completed
            if status == "exit" and status_detail == "finished":
                pr_url = _extract_pr_url(session_data)
                update_session_status(session_id, "completed", pr_url=pr_url)
                logger.info(
                    f"Session {session_id} completed — PR: {pr_url or 'none'}",
                    extra={**log_extra, "event_type": "session_completed"},
                )
                return

            # v3: "error" or "suspended" are terminal failure states
            if status in ("error", "suspended"):
                reason = status_detail or status
                update_session_status(
                    session_id,
                    "failed",
                    error_message=f"Devin session reached terminal status: {status} ({reason})",
                    error_type="devin_terminal",
                )
                logger.warning(
                    f"Session {session_id} ended with status: {status} ({reason})",
                    extra={**log_extra, "event_type": "session_failed"},
                )
                return

            # v3: "exit" without "finished" is also terminal
            if status == "exit":
                pr_url = _extract_pr_url(session_data)
                update_session_status(session_id, "completed", pr_url=pr_url)
                logger.info(
                    f"Session {session_id} exited (detail: {status_detail}) — PR: {pr_url or 'none'}",
                    extra={**log_extra, "event_type": "session_completed"},
                )
                return

            # Non-terminal: new, creating, claimed, running, resuming — keep polling

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
