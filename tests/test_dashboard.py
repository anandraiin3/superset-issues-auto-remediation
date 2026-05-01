"""Tests for the operations dashboard."""

import os
import unittest

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")

from app import create_app
from src.database import (
    create_session,
    init_db,
    reserve_issue,
    reset_connection,
    update_session_status,
)


class DashboardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        reset_connection()
        self.app = create_app()
        self.client = self.app.test_client()
        init_db()

    def test_dashboard_loads(self) -> None:
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Remediation Operations Dashboard", resp.data)

    def test_dashboard_shows_sessions(self) -> None:
        reserve_issue(100, "Bug 100", "https://github.com/t/r")
        create_session("s-d1", 100, "Bug 100", "https://github.com/t/r")
        update_session_status(
            "s-d1", "completed", pr_url="https://github.com/t/r/pull/100"
        )
        resp = self.client.get("/dashboard")
        self.assertIn(b"Bug 100", resp.data)
        self.assertIn(b"PR</a>", resp.data)

    def test_dashboard_status_filter(self) -> None:
        reserve_issue(200, "Bug 200", "https://github.com/t/r")
        create_session("s-d2", 200, "Bug 200", "https://github.com/t/r")
        update_session_status("s-d2", "failed", error_message="err", error_type="e")
        resp = self.client.get("/dashboard?status=failed")
        self.assertIn(b"Bug 200", resp.data)
        resp_completed = self.client.get("/dashboard?status=completed")
        self.assertNotIn(b"Bug 200", resp_completed.data)

    def test_dashboard_shows_status_detail(self) -> None:
        reserve_issue(300, "Bug 300", "https://github.com/t/r")
        create_session(
            "s-d3",
            300,
            "Bug 300",
            "https://github.com/t/r",
            devin_url="https://app.devin.ai/sessions/s-d3",
        )
        update_session_status(
            "s-d3",
            "running",
            status_detail="waiting_for_user",
        )
        resp = self.client.get("/dashboard")
        self.assertIn(b"waiting for user", resp.data)
        self.assertIn(b"Devin</a>", resp.data)  # Devin session link

    def test_dashboard_shows_devin_link(self) -> None:
        reserve_issue(400, "Feature 400", "https://github.com/t/r")
        create_session(
            "s-d4",
            400,
            "Feature 400",
            "https://github.com/t/r",
            devin_url="https://app.devin.ai/sessions/s-d4",
        )
        resp = self.client.get("/dashboard")
        self.assertIn(b"app.devin.ai/sessions/s-d4", resp.data)

    def test_dashboard_issue_link(self) -> None:
        reserve_issue(500, "Bug 500", "https://github.com/t/r")
        create_session("s-d5", 500, "Bug 500", "https://github.com/t/r")
        resp = self.client.get("/dashboard")
        self.assertIn(b"https://github.com/t/r/issues/500", resp.data)

    def test_dashboard_shows_cost(self) -> None:
        reserve_issue(600, "Bug 600", "https://github.com/t/r")
        create_session("s-d6", 600, "Bug 600", "https://github.com/t/r")
        update_session_status("s-d6", "completed", acus_consumed=4.75)
        resp = self.client.get("/dashboard")
        self.assertIn(b"4.75", resp.data)
        self.assertIn(b"Total Cost", resp.data)

    def test_health_endpoint(self) -> None:
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
