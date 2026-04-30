"""GitHub webhook listener.

WH-01 – WH-08: Accepts POST on /webhook, validates HMAC-SHA256
signature, filters for configured issue labels (bug, feature, task,
etc.), and dispatches remediation asynchronously.
"""

import hashlib
import hmac
import threading
from typing import Any, Optional

from flask import Blueprint, Response, request

from src.config import Config
from src.logger import get_logger
from src.orchestrator import remediate_issue

logger = get_logger(__name__)

webhook_bp = Blueprint("webhook", __name__)


def _verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """WH-02: Validate GitHub HMAC-SHA256 webhook signature."""
    if not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        Config.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)


def _process_job(
    repo_url: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
    issue_labels: list[str],
) -> None:
    """Run remediation in a daemon thread (WH-06)."""
    thread = threading.Thread(
        target=remediate_issue,
        args=(repo_url, issue_number, issue_title, issue_body, issue_labels),
        daemon=True,
    )
    thread.start()
    logger.info(
        f"Dispatched remediation thread for issue #{issue_number}",
        extra={"issue_number": issue_number, "event_type": "job_dispatched"},
    )


def _get_matching_labels(issue: dict[str, Any]) -> list[str]:
    """Return the list of issue label names that match configured labels."""
    labels = issue.get("labels", [])
    issue_label_names = [lbl.get("name", "") for lbl in labels]
    return [name for name in issue_label_names if name in Config.ISSUE_LABELS]


def _get_issue_type(labels: list[str]) -> Optional[str]:
    """Derive the primary issue type from matched labels."""
    if not labels:
        return None
    return labels[0]


@webhook_bp.route("/webhook", methods=["POST"])
def handle_webhook() -> tuple[Response, int]:
    """WH-01 / WH-03: Accept webhook, return 200 immediately."""
    # WH-02: Signature validation (NF-07)
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_signature(request.data, signature):
        logger.warning(
            "Invalid webhook signature",
            extra={"event_type": "signature_invalid"},
        )
        return Response("Invalid signature", status=403)

    # WH-07: Graceful handling of malformed payloads
    try:
        payload: dict[str, Any] = request.get_json(force=True)
    except Exception:
        logger.warning(
            "Malformed webhook payload",
            extra={"event_type": "payload_malformed"},
        )
        return Response("OK", status=200)

    if not isinstance(payload, dict):
        logger.warning(
            "Webhook payload is not a JSON object",
            extra={"event_type": "payload_malformed"},
        )
        return Response("OK", status=200)

    # WH-04: Only process issues.opened or issues.labeled
    event_type = request.headers.get("X-GitHub-Event", "")
    action = payload.get("action", "")

    if event_type != "issues" or action not in ("opened", "labeled"):
        logger.info(
            f"Ignoring event: {event_type}.{action}",
            extra={"event_type": "event_filtered"},
        )
        return Response("OK", status=200)

    issue: dict[str, Any] = payload.get("issue", {})
    if not issue:
        return Response("OK", status=200)

    # WH-05 / WH-08: Only trigger for issues with at least one configured label
    matching_labels = _get_matching_labels(issue)
    if not matching_labels:
        logger.info(
            f"Issue #{issue.get('number')} has no matching labels "
            f"(configured: {Config.ISSUE_LABELS}) — skipping",
            extra={
                "issue_number": issue.get("number"),
                "event_type": "label_missing",
            },
        )
        return Response("OK", status=200)

    repo_url = payload.get("repository", {}).get("html_url", Config.REPOSITORY_URL)
    issue_number: int = issue["number"]
    issue_title: str = issue.get("title", "")
    issue_body: str = issue.get("body", "") or ""

    logger.info(
        f"Accepted issue #{issue_number}: {issue_title} (labels: {matching_labels})",
        extra={"issue_number": issue_number, "event_type": "issue_accepted"},
    )

    # WH-06: Asynchronous processing
    _process_job(repo_url, issue_number, issue_title, issue_body, matching_labels)

    # WH-03: Return 200 immediately
    return Response("OK", status=200)
