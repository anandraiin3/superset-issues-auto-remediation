"""Auto-register GitHub webhook on application startup.

Uses the GitHub REST API to idempotently create a webhook on the
configured repository.  Requires GITHUB_TOKEN with Webhooks: Read & Write
permission and APP_BASE_URL to be set.
"""

import re
from typing import Optional

import requests

from src.config import Config
from src.logger import get_logger

logger = get_logger(__name__)


def _extract_owner_repo(repo_url: str) -> Optional[str]:
    """Extract 'owner/repo' from a GitHub URL."""
    match = re.search(r"github\.com/([^/]+/[^/]+)", repo_url)
    if not match:
        return None
    return match.group(1).rstrip("/")


def _list_hooks(owner_repo: str) -> list[dict]:
    """List existing webhooks on the repository."""
    url = f"https://api.github.com/repos/{owner_repo}/hooks"
    resp = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _webhook_exists(owner_repo: str, target_url: str) -> Optional[int]:
    """Check if a webhook with the given URL already exists.

    Returns the hook ID if found, None otherwise.
    """
    hooks = _list_hooks(owner_repo)
    for hook in hooks:
        config = hook.get("config", {})
        if config.get("url") == target_url:
            return hook.get("id")
    return None


def _create_hook(owner_repo: str, target_url: str) -> dict:
    """Create a new webhook on the repository."""
    url = f"https://api.github.com/repos/{owner_repo}/hooks"
    payload = {
        "name": "web",
        "active": True,
        "events": ["issues"],
        "config": {
            "url": target_url,
            "content_type": "json",
            "secret": Config.GITHUB_WEBHOOK_SECRET,
            "insecure_ssl": "0",
        },
    }
    resp = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _update_hook(owner_repo: str, hook_id: int, target_url: str) -> dict:
    """Update an existing webhook to ensure config is current."""
    url = f"https://api.github.com/repos/{owner_repo}/hooks/{hook_id}"
    payload = {
        "active": True,
        "events": ["issues"],
        "config": {
            "url": target_url,
            "content_type": "json",
            "secret": Config.GITHUB_WEBHOOK_SECRET,
            "insecure_ssl": "0",
        },
    }
    resp = requests.patch(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def register_webhook() -> bool:
    """Idempotently register a webhook on the configured repository.

    Returns True if the webhook was created or already exists.
    Returns False if registration was skipped (missing config) or failed.
    """
    if not Config.APP_BASE_URL:
        logger.info(
            "APP_BASE_URL not set — skipping automatic webhook registration",
            extra={"event_type": "webhook_registration_skipped"},
        )
        return False

    if not Config.GITHUB_TOKEN:
        logger.warning(
            "GITHUB_TOKEN not set — cannot register webhook",
            extra={"event_type": "webhook_registration_skipped"},
        )
        return False

    owner_repo = _extract_owner_repo(Config.REPOSITORY_URL)
    if not owner_repo:
        logger.error(
            f"Cannot extract owner/repo from REPOSITORY_URL: {Config.REPOSITORY_URL}",
            extra={"event_type": "webhook_registration_error"},
        )
        return False

    target_url = f"{Config.APP_BASE_URL.rstrip('/')}/webhook"

    try:
        existing_id = _webhook_exists(owner_repo, target_url)
        if existing_id:
            _update_hook(owner_repo, existing_id, target_url)
            logger.info(
                f"Webhook already exists (id={existing_id}) — updated config",
                extra={
                    "event_type": "webhook_updated",
                    "hook_id": existing_id,
                    "target_url": target_url,
                },
            )
            return True

        try:
            result = _create_hook(owner_repo, target_url)
        except requests.HTTPError as create_exc:
            if create_exc.response is not None and create_exc.response.status_code == 422:
                logger.info(
                    f"Webhook already exists on {owner_repo} (duplicate registration ignored)",
                    extra={"event_type": "webhook_already_exists"},
                )
                return True
            raise

        hook_id = result.get("id")
        logger.info(
            f"Webhook registered on {owner_repo} (id={hook_id})",
            extra={
                "event_type": "webhook_registered",
                "hook_id": hook_id,
                "target_url": target_url,
            },
        )
        return True

    except requests.HTTPError as exc:
        logger.error(
            f"Failed to register webhook on {owner_repo}: {exc}",
            extra={"event_type": "webhook_registration_error"},
            exc_info=True,
        )
        return False
    except requests.RequestException as exc:
        logger.error(
            f"Network error registering webhook on {owner_repo}: {exc}",
            extra={"event_type": "webhook_registration_error"},
            exc_info=True,
        )
        return False
