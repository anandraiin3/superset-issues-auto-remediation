"""Tests for the operations dashboard."""

import os
import unittest

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")

from app import create_app
from src.database import create_session, init_db, update_session_status


class DashboardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()
        init_db()

    def test_dashboard_loads(self) -> None:
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Vulnerability Remediation Dashboard", resp.data)

    def test_dashboard_shows_sessions(self) -> None:
        create_session("s-d1", 100, "Bug 100", "https://github.com/t/r")
        update_session_status(
            "s-d1", "completed", pr_url="https://github.com/t/r/pull/100"
        )
        resp = self.client.get("/dashboard")
        self.assertIn(b"Bug 100", resp.data)
        self.assertIn(b"View PR", resp.data)

    def test_dashboard_status_filter(self) -> None:
        create_session("s-d2", 200, "Bug 200", "https://github.com/t/r")
        update_session_status("s-d2", "failed", error_message="err", error_type="e")
        resp = self.client.get("/dashboard?status=failed")
        self.assertIn(b"Bug 200", resp.data)
        resp_completed = self.client.get("/dashboard?status=completed")
        self.assertNotIn(b"Bug 200", resp_completed.data)

    def test_health_endpoint(self) -> None:
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
