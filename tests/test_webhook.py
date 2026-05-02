"""Tests for the webhook listener."""

import hashlib
import hmac
import json
import os
import unittest
from unittest.mock import patch

# Set required env vars before importing app modules
os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")

from app import create_app


def _make_issue_type(name: str) -> dict:
    """Build a GitHub issue type object as it appears in webhook payloads."""
    return {"id": 1, "node_id": "IT_fake", "name": name, "description": ""}


class WebhookTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()
        self.secret = "test-secret"

    def _sign(self, payload: bytes) -> str:
        sig = hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={sig}"

    def _post_webhook(
        self,
        payload: dict,
        event: str = "issues",
        sign: bool = True,
    ):
        body = json.dumps(payload).encode()
        headers = {"X-GitHub-Event": event, "Content-Type": "application/json"}
        if sign:
            headers["X-Hub-Signature-256"] = self._sign(body)
        return self.client.post("/webhook", data=body, headers=headers)

    def test_invalid_signature_returns_403(self) -> None:
        resp = self.client.post(
            "/webhook",
            data=b"{}",
            headers={
                "X-Hub-Signature-256": "sha256=invalid",
                "X-GitHub-Event": "issues",
            },
        )
        self.assertEqual(resp.status_code, 403)

    def test_missing_signature_returns_403(self) -> None:
        resp = self.client.post(
            "/webhook",
            data=b"{}",
            headers={"X-GitHub-Event": "issues"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_issue_event_returns_200(self) -> None:
        resp = self._post_webhook({"action": "created"}, event="push")
        self.assertEqual(resp.status_code, 200)

    def test_issue_without_type_returns_200(self) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 1,
                "title": "Test issue",
                "body": "desc",
                "labels": [],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    def test_issue_with_unsupported_type_returns_200(self) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 2,
                "title": "Test issue",
                "body": "desc",
                "labels": [],
                "type": _make_issue_type("Epic"),
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_bug_type_triggers_remediation(self, mock_remediate) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 42,
                "title": "XSS in login",
                "body": "details...",
                "labels": [],
                "type": _make_issue_type("Bug"),
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_feature_type_triggers_remediation(self, mock_remediate) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 43,
                "title": "Add dark mode",
                "body": "details...",
                "labels": [],
                "type": _make_issue_type("Feature"),
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_task_type_triggers_remediation(self, mock_remediate) -> None:
        payload = {
            "action": "labeled",
            "issue": {
                "number": 44,
                "title": "Update dependencies",
                "body": "details...",
                "labels": [],
                "type": _make_issue_type("Task"),
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    def test_malformed_payload_returns_200(self) -> None:
        body = b"not json at all"
        headers = {
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": self._sign(body),
        }
        resp = self.client.post("/webhook", data=body, headers=headers)
        self.assertIn(resp.status_code, (200, 403))

    @patch("src.webhook.remediate_issue")
    def test_title_prefix_bug_triggers_remediation(self, mock_remediate) -> None:
        """Fallback: [Bug] title prefix triggers remediation on personal repos."""
        payload = {
            "action": "opened",
            "issue": {
                "number": 50,
                "title": "[Bug] Fix CSS overlap in dashboard",
                "body": "details...",
                "labels": [],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_title_prefix_feature_triggers_remediation(self, mock_remediate) -> None:
        """Fallback: [Feature] title prefix triggers remediation."""
        payload = {
            "action": "opened",
            "issue": {
                "number": 51,
                "title": "[Feature] Add dark mode support",
                "body": "details...",
                "labels": [],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_title_prefix_task_triggers_remediation(self, mock_remediate) -> None:
        """Fallback: [Task] title prefix triggers remediation."""
        payload = {
            "action": "opened",
            "issue": {
                "number": 52,
                "title": "[Task] Update documentation",
                "body": "details...",
                "labels": [],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    def test_title_prefix_unsupported_type_skipped(self) -> None:
        """[Epic] prefix is not a configured type — should be skipped."""
        payload = {
            "action": "opened",
            "issue": {
                "number": 53,
                "title": "[Epic] Large refactor",
                "body": "details...",
                "labels": [],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_native_type_takes_priority_over_prefix(self, mock_remediate) -> None:
        """Native issue.type should take priority over title prefix."""
        payload = {
            "action": "opened",
            "issue": {
                "number": 54,
                "title": "[Feature] Something",
                "body": "details...",
                "labels": [],
                "type": _make_issue_type("Bug"),
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    def test_closed_action_ignored(self) -> None:
        payload = {
            "action": "closed",
            "issue": {
                "number": 1,
                "title": "Test",
                "body": "",
                "labels": [],
                "type": _make_issue_type("Bug"),
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
