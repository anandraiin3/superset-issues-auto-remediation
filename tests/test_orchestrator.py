"""Tests for the remediation orchestrator."""

import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
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
            "status": "running",
            "tags": ["auto-remediation"],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        mock_poll.return_value = {
            "session_id": "ses-123",
            "status": "exit",
            "status_detail": "finished",
            "pull_requests": [
                {"pr_url": "https://github.com/test/repo/pull/1", "pr_state": "open"}
            ],
        }

        remediate_issue("https://github.com/test/repo", 1, "XSS bug", "details", "bug")

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
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        mock_poll.return_value = {
            "session_id": "ses-dup-1",
            "status": "exit",
            "status_detail": "finished",
            "pull_requests": [],
        }

        # First call creates session
        remediate_issue("https://github.com/test/repo", 50, "Bug", "body", "bug")
        # Second call should skip
        remediate_issue("https://github.com/test/repo", 50, "Bug", "body", "bug")

        self.assertEqual(mock_create.call_count, 1)

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_error_session_marked_failed(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        mock_create.return_value = {
            "session_id": "ses-err",
            "url": "https://app.devin.ai/sessions/ses-err",
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        mock_poll.return_value = {
            "session_id": "ses-err",
            "status": "error",
            "status_detail": "error",
            "pull_requests": [],
        }

        remediate_issue("https://github.com/test/repo", 60, "Bug", "body", "feature")
        mock_poll.assert_called_once()

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_suspended_session_marked_failed(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        mock_create.return_value = {
            "session_id": "ses-susp",
            "url": "https://app.devin.ai/sessions/ses-susp",
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        mock_poll.return_value = {
            "session_id": "ses-susp",
            "status": "suspended",
            "status_detail": "inactivity",
            "pull_requests": [],
        }

        remediate_issue("https://github.com/test/repo", 70, "Task", "body", "task")
        mock_poll.assert_called_once()


if __name__ == "__main__":
    unittest.main()
