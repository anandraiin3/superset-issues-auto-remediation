"""Tests for the remediation orchestrator."""

import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")
os.environ["POLLING_INTERVAL_SECONDS"] = "0"
os.environ["SESSION_TIMEOUT_MINUTES"] = "1"

from src.database import init_db, reset_connection
from src.orchestrator import remediate_issue


class OrchestratorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        reset_connection()
        init_db()

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_successful_remediation(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        mock_create.return_value = {
            "session_id": "ses-123",
            "url": "https://app.devin.ai/sessions/ses-123",
            "is_new_session": True,
        }
        mock_poll.return_value = {
            "status_enum": "finished",
            "pull_request": {"url": "https://github.com/test/repo/pull/1"},
        }

        remediate_issue(
            "https://github.com/test/repo", 1, "XSS bug", "details", ["bug"]
        )

        mock_create.assert_called_once()
        mock_poll.assert_called_once()

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_idempotency_skips_duplicate(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        mock_create.return_value = {
            "session_id": "ses-dup-1",
            "url": "https://app.devin.ai/sessions/ses-dup-1",
        }
        mock_poll.return_value = {"status_enum": "finished", "pull_request": None}

        # First call creates session
        remediate_issue("https://github.com/test/repo", 50, "Bug", "body", ["bug"])
        # Second call should skip
        remediate_issue("https://github.com/test/repo", 50, "Bug", "body", ["bug"])

        self.assertEqual(mock_create.call_count, 1)

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_expired_session_marked_failed(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        mock_create.return_value = {
            "session_id": "ses-exp",
            "url": "https://app.devin.ai/sessions/ses-exp",
        }
        mock_poll.return_value = {"status_enum": "expired", "pull_request": None}

        remediate_issue("https://github.com/test/repo", 60, "Bug", "body", ["feature"])
        mock_poll.assert_called_once()


if __name__ == "__main__":
    unittest.main()
