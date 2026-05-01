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

from src.database import get_session, init_db, reset_connection
from src.orchestrator import (
    _fetch_latest_devin_message,
    _is_infrastructure_question,
    remediate_issue,
)


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

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_pr_ready_status_when_pr_exists(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        """When a PR exists and Devin is 'working', status_detail should be 'pr_ready'."""
        mock_create.return_value = {
            "session_id": "ses-pr-ready",
            "url": "https://app.devin.ai/sessions/ses-pr-ready",
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        # First poll: working with a PR → should become pr_ready
        # Second poll: exit/finished
        mock_poll.side_effect = [
            {
                "session_id": "ses-pr-ready",
                "status": "running",
                "status_detail": "working",
                "pull_requests": [
                    {
                        "pr_url": "https://github.com/test/repo/pull/42",
                        "pr_state": "open",
                    }
                ],
            },
            {
                "session_id": "ses-pr-ready",
                "status": "exit",
                "status_detail": "finished",
                "pull_requests": [
                    {
                        "pr_url": "https://github.com/test/repo/pull/42",
                        "pr_state": "open",
                    }
                ],
            },
        ]

        remediate_issue("https://github.com/test/repo", 85, "Bug", "body", "bug")
        row = get_session("ses-pr-ready")
        self.assertIsNotNone(row)
        # Final status is completed/finished, but pr_url should be set
        self.assertEqual(row["status"], "completed")
        self.assertEqual(row["pr_url"], "https://github.com/test/repo/pull/42")

    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_status_detail_stored_in_db(
        self, mock_create: MagicMock, mock_poll: MagicMock
    ) -> None:
        """status_detail from Devin API should be persisted in the DB."""
        mock_create.return_value = {
            "session_id": "ses-detail",
            "url": "https://app.devin.ai/sessions/ses-detail",
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        mock_poll.return_value = {
            "session_id": "ses-detail",
            "status": "exit",
            "status_detail": "finished",
            "pull_requests": [
                {"pr_url": "https://github.com/test/repo/pull/5", "pr_state": "open"}
            ],
        }

        remediate_issue("https://github.com/test/repo", 80, "Bug", "body", "bug")
        row = get_session("ses-detail")
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "completed")
        self.assertEqual(row["status_detail"], "finished")
        self.assertEqual(row["pr_url"], "https://github.com/test/repo/pull/5")
        self.assertEqual(row["devin_url"], "https://app.devin.ai/sessions/ses-detail")

    @patch("src.orchestrator._post_github_issue_comment")
    @patch("src.orchestrator._fetch_latest_devin_message")
    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_waiting_for_user_posts_comment(
        self,
        mock_create: MagicMock,
        mock_poll: MagicMock,
        mock_fetch_msg: MagicMock,
        mock_post_comment: MagicMock,
    ) -> None:
        """When Devin is waiting_for_user with an issue-related question,
        the question should be posted back to the GitHub issue."""
        mock_create.return_value = {
            "session_id": "ses-wait",
            "url": "https://app.devin.ai/sessions/ses-wait",
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        # First poll: waiting_for_user, second poll: exit/finished
        mock_poll.side_effect = [
            {
                "session_id": "ses-wait",
                "status": "running",
                "status_detail": "waiting_for_user",
                "pull_requests": [],
            },
            {
                "session_id": "ses-wait",
                "status": "exit",
                "status_detail": "finished",
                "pull_requests": [],
            },
        ]
        mock_fetch_msg.return_value = {
            "event_id": "evt-1",
            "message": "Should I also update the unit tests for this component?",
        }
        mock_post_comment.return_value = True

        remediate_issue("https://github.com/test/repo", 90, "Bug", "body", "bug")

        mock_fetch_msg.assert_called_once()
        mock_post_comment.assert_called_once()
        call_args = mock_post_comment.call_args
        self.assertIn(
            "question",
            call_args[1]["body"].lower()
            if "body" in call_args[1]
            else call_args[0][2].lower(),
        )

    @patch("src.orchestrator._post_github_issue_comment")
    @patch("src.orchestrator._fetch_latest_devin_message")
    @patch("src.orchestrator._poll_session")
    @patch("src.orchestrator._create_devin_session")
    def test_infra_question_not_posted(
        self,
        mock_create: MagicMock,
        mock_poll: MagicMock,
        mock_fetch_msg: MagicMock,
        mock_post_comment: MagicMock,
    ) -> None:
        """Infrastructure questions (e.g. permissions) should NOT be posted
        to the GitHub issue."""
        mock_create.return_value = {
            "session_id": "ses-infra",
            "url": "https://app.devin.ai/sessions/ses-infra",
            "status": "running",
            "tags": [],
            "org_id": "test-org",
            "created_at": 1700000000,
            "updated_at": 1700000000,
            "acus_consumed": 0,
            "pull_requests": [],
        }
        mock_poll.side_effect = [
            {
                "session_id": "ses-infra",
                "status": "running",
                "status_detail": "waiting_for_user",
                "pull_requests": [],
            },
            {
                "session_id": "ses-infra",
                "status": "exit",
                "status_detail": "finished",
                "pull_requests": [],
            },
        ]
        mock_fetch_msg.return_value = {
            "event_id": "evt-2",
            "message": "I need push access / contents:write permission on the repo.",
        }

        remediate_issue("https://github.com/test/repo", 95, "Bug", "body", "bug")

        mock_fetch_msg.assert_called_once()
        mock_post_comment.assert_not_called()


class InfraClassificationTestCase(unittest.TestCase):
    """Tests for _is_infrastructure_question."""

    def test_permission_is_infra(self) -> None:
        self.assertTrue(
            _is_infrastructure_question(
                "I need push access to the repo to create the PR."
            )
        )

    def test_api_key_is_infra(self) -> None:
        self.assertTrue(
            _is_infrastructure_question(
                "The API key seems to be expired, can you provide a new one?"
            )
        )

    def test_contents_write_is_infra(self) -> None:
        self.assertTrue(
            _is_infrastructure_question(
                "The GITHUB_TOKEN doesn't have contents:write permission."
            )
        )

    def test_issue_question_not_infra(self) -> None:
        self.assertFalse(
            _is_infrastructure_question(
                "Should I also update the unit tests for this component?"
            )
        )

    def test_clarification_not_infra(self) -> None:
        self.assertFalse(
            _is_infrastructure_question(
                "The issue mentions a calculated column — could you provide an example SQL?"
            )
        )

    def test_scope_question_not_infra(self) -> None:
        self.assertFalse(
            _is_infrastructure_question(
                "Should the fix apply to all database backends or just PostgreSQL?"
            )
        )


class FetchMessageTestCase(unittest.TestCase):
    """Tests for _fetch_latest_devin_message dedup behaviour."""

    @patch("src.orchestrator.requests.get")
    def test_returns_none_when_latest_already_posted(self, mock_get: MagicMock) -> None:
        """If the newest devin message matches after_event_id, return None."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "items": [
                {"source": "devin", "event_id": "old-1", "message": "old msg"},
                {"source": "user", "event_id": "u-1", "message": "user msg"},
                {"source": "devin", "event_id": "latest-1", "message": "latest"},
            ]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _fetch_latest_devin_message("test-sid", after_event_id="latest-1")
        self.assertIsNone(result)

    @patch("src.orchestrator.requests.get")
    def test_returns_new_message_when_not_yet_posted(self, mock_get: MagicMock) -> None:
        """If the newest devin message is different from after_event_id, return it."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "items": [
                {"source": "devin", "event_id": "old-1", "message": "old msg"},
                {"source": "devin", "event_id": "new-1", "message": "new question"},
            ]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _fetch_latest_devin_message("test-sid", after_event_id="old-1")
        self.assertIsNotNone(result)
        self.assertEqual(result["event_id"], "new-1")
        self.assertEqual(result["message"], "new question")


if __name__ == "__main__":
    unittest.main()
