"""Tests for the observability store."""

import os
import unittest

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")

from src.database import (
    create_session,
    get_all_sessions,
    get_dashboard_stats,
    get_sessions_by_status,
    init_db,
    reserve_issue,
    reset_connection,
    session_exists_for_issue,
    update_session_status,
)


class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        reset_connection()
        init_db()

    def test_create_and_query_session(self) -> None:
        reserve_issue(1, "XSS bug", "https://github.com/t/r")
        create_session("s-001", 1, "XSS bug", "https://github.com/t/r")
        self.assertTrue(session_exists_for_issue(1))
        self.assertFalse(session_exists_for_issue(999))

    def test_update_status_to_completed(self) -> None:
        reserve_issue(2, "SQLi", "https://github.com/t/r")
        create_session("s-002", 2, "SQLi", "https://github.com/t/r")
        update_session_status("s-002", "running")
        update_session_status(
            "s-002", "completed", pr_url="https://github.com/t/r/pull/1"
        )
        sessions = get_sessions_by_status("completed")
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["pr_url"], "https://github.com/t/r/pull/1")
        self.assertIsNotNone(sessions[0]["time_to_remediation_seconds"])

    def test_update_status_to_failed(self) -> None:
        reserve_issue(3, "CSRF", "https://github.com/t/r")
        create_session("s-003", 3, "CSRF", "https://github.com/t/r")
        update_session_status(
            "s-003",
            "failed",
            error_message="API error",
            error_type="api_error",
        )
        sessions = get_sessions_by_status("failed")
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["error_message"], "API error")

    def test_dashboard_stats(self) -> None:
        reserve_issue(10, "Bug A", "https://github.com/t/r")
        create_session("s-010", 10, "Bug A", "https://github.com/t/r")
        reserve_issue(11, "Bug B", "https://github.com/t/r")
        create_session("s-011", 11, "Bug B", "https://github.com/t/r")
        update_session_status("s-010", "completed")
        update_session_status("s-011", "failed", error_message="err", error_type="e")

        stats = get_dashboard_stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["failed"], 1)
        self.assertGreater(stats["success_rate"], 0)

    def test_get_all_sessions(self) -> None:
        reserve_issue(20, "Bug X", "https://github.com/t/r")
        create_session("s-020", 20, "Bug X", "https://github.com/t/r")
        reserve_issue(21, "Bug Y", "https://github.com/t/r")
        create_session("s-021", 21, "Bug Y", "https://github.com/t/r")
        all_sessions = get_all_sessions()
        self.assertEqual(len(all_sessions), 2)

    def test_reserve_issue_prevents_duplicates(self) -> None:
        """reserve_issue should return False for a duplicate issue number."""
        self.assertTrue(reserve_issue(30, "Bug Z", "https://github.com/t/r"))
        self.assertFalse(reserve_issue(30, "Bug Z dup", "https://github.com/t/r"))

    def test_acus_consumed_tracked(self) -> None:
        """ACU consumption should be stored and aggregated."""
        reserve_issue(40, "Bug ACU", "https://github.com/t/r")
        create_session("s-040", 40, "Bug ACU", "https://github.com/t/r")
        update_session_status("s-040", "running", acus_consumed=1.5)
        update_session_status("s-040", "completed", acus_consumed=3.25)
        from src.database import get_session

        row = get_session("s-040")
        self.assertIsNotNone(row)
        self.assertEqual(row["acus_consumed"], 3.25)

    def test_dashboard_stats_total_cost(self) -> None:
        """Dashboard stats should include total_cost_acus."""
        reserve_issue(50, "Bug C", "https://github.com/t/r")
        create_session("s-050", 50, "Bug C", "https://github.com/t/r")
        update_session_status("s-050", "completed", acus_consumed=2.0)
        reserve_issue(51, "Bug D", "https://github.com/t/r")
        create_session("s-051", 51, "Bug D", "https://github.com/t/r")
        update_session_status("s-051", "completed", acus_consumed=1.5)
        stats = get_dashboard_stats()
        self.assertEqual(stats["total_cost_acus"], 3.5)


if __name__ == "__main__":
    unittest.main()
