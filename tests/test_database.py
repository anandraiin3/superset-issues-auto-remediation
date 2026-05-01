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

    def test_devin_started_at_set_on_create_session(self) -> None:
        """create_session should record devin_started_at timestamp."""
        from src.database import get_session

        reserve_issue(60, "Bug E", "https://github.com/t/r")
        create_session("s-060", 60, "Bug E", "https://github.com/t/r")
        row = get_session("s-060")
        self.assertIsNotNone(row)
        self.assertIsNotNone(row["devin_started_at"])

    def test_pr_raised_at_set_on_first_pr_url(self) -> None:
        """pr_raised_at should be set the first time a PR URL appears."""
        from src.database import get_session

        reserve_issue(61, "Bug F", "https://github.com/t/r")
        create_session("s-061", 61, "Bug F", "https://github.com/t/r")
        # First update with PR URL
        update_session_status(
            "s-061", "running", pr_url="https://github.com/t/r/pull/99"
        )
        row = get_session("s-061")
        self.assertIsNotNone(row)
        self.assertIsNotNone(row["pr_raised_at"])
        first_pr_time = row["pr_raised_at"]

        # Second update should NOT overwrite pr_raised_at
        update_session_status(
            "s-061", "completed", pr_url="https://github.com/t/r/pull/99"
        )
        row = get_session("s-061")
        self.assertEqual(row["pr_raised_at"], first_pr_time)

    def test_duration_fields_computed(self) -> None:
        """get_all_sessions should include overall_time_ms and devin_time_ms."""
        import time

        reserve_issue(62, "Bug G", "https://github.com/t/r")
        create_session("s-062", 62, "Bug G", "https://github.com/t/r")
        time.sleep(0.05)  # small delay to ensure non-zero durations
        update_session_status(
            "s-062", "running", pr_url="https://github.com/t/r/pull/100"
        )
        time.sleep(0.05)
        update_session_status("s-062", "completed")
        sessions = get_all_sessions()
        s = next(x for x in sessions if x["session_id"] == "s-062")
        # overall_time_ms should be set (webhook → PR)
        self.assertIsNotNone(s["overall_time_ms"])
        self.assertGreaterEqual(s["overall_time_ms"], 0)
        # devin_time_ms should be set (session creation → completion)
        self.assertIsNotNone(s["devin_time_ms"])
        self.assertGreaterEqual(s["devin_time_ms"], 0)

    def test_duration_none_when_no_pr(self) -> None:
        """overall_time_ms should be None when no PR has been raised."""
        reserve_issue(63, "Bug H", "https://github.com/t/r")
        create_session("s-063", 63, "Bug H", "https://github.com/t/r")
        update_session_status("s-063", "failed", error_message="err", error_type="e")
        sessions = get_all_sessions()
        s = next(x for x in sessions if x["session_id"] == "s-063")
        self.assertIsNone(s["overall_time_ms"])


if __name__ == "__main__":
    unittest.main()
