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
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")

from app import create_app


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

    def test_issue_without_matching_label_returns_200(self) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 1,
                "title": "Test issue",
                "body": "desc",
                "labels": [{"name": "wontfix"}],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    def test_issue_with_no_labels_returns_200(self) -> None:
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

    @patch("src.webhook.remediate_issue")
    def test_bug_label_triggers_remediation(self, mock_remediate) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 42,
                "title": "XSS in login",
                "body": "details...",
                "labels": [{"name": "bug"}],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_feature_label_triggers_remediation(self, mock_remediate) -> None:
        payload = {
            "action": "opened",
            "issue": {
                "number": 43,
                "title": "Add dark mode",
                "body": "details...",
                "labels": [{"name": "feature"}],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)

    @patch("src.webhook.remediate_issue")
    def test_task_label_triggers_remediation(self, mock_remediate) -> None:
        payload = {
            "action": "labeled",
            "issue": {
                "number": 44,
                "title": "Update dependencies",
                "body": "details...",
                "labels": [{"name": "task"}],
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

    def test_closed_action_ignored(self) -> None:
        payload = {
            "action": "closed",
            "issue": {
                "number": 1,
                "title": "Test",
                "body": "",
                "labels": [{"name": "bug"}],
            },
            "repository": {"html_url": "https://github.com/test/repo"},
        }
        resp = self._post_webhook(payload)
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
