"""Tests for automatic webhook registration."""

import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")
os.environ.setdefault("DATABASE_PATH", ":memory:")

from src.webhook_registration import (
    _extract_owner_repo,
    _webhook_exists,
    register_webhook,
)


class ExtractOwnerRepoTestCase(unittest.TestCase):
    def test_https_url(self) -> None:
        self.assertEqual(
            _extract_owner_repo("https://github.com/owner/repo"), "owner/repo"
        )

    def test_trailing_slash(self) -> None:
        self.assertEqual(
            _extract_owner_repo("https://github.com/owner/repo/"), "owner/repo"
        )

    def test_invalid_url(self) -> None:
        self.assertIsNone(_extract_owner_repo("https://gitlab.com/owner/repo"))

    def test_empty_url(self) -> None:
        self.assertIsNone(_extract_owner_repo(""))


class RegisterWebhookTestCase(unittest.TestCase):
    @patch("src.webhook_registration.Config")
    def test_skips_when_no_app_base_url(self, mock_config: MagicMock) -> None:
        mock_config.APP_BASE_URL = ""
        mock_config.GITHUB_TOKEN = "tok"
        mock_config.REPOSITORY_URL = "https://github.com/test/repo"
        result = register_webhook()
        self.assertFalse(result)

    @patch("src.webhook_registration.Config")
    def test_skips_when_no_github_token(self, mock_config: MagicMock) -> None:
        mock_config.APP_BASE_URL = "https://example.com"
        mock_config.GITHUB_TOKEN = ""
        result = register_webhook()
        self.assertFalse(result)

    @patch("src.webhook_registration._create_hook")
    @patch("src.webhook_registration._webhook_exists", return_value=None)
    @patch("src.webhook_registration.Config")
    def test_creates_new_webhook(
        self,
        mock_config: MagicMock,
        mock_exists: MagicMock,
        mock_create: MagicMock,
    ) -> None:
        mock_config.APP_BASE_URL = "https://example.com"
        mock_config.GITHUB_TOKEN = "tok"
        mock_config.REPOSITORY_URL = "https://github.com/test/repo"
        mock_config.GITHUB_WEBHOOK_SECRET = "secret"
        mock_create.return_value = {"id": 123}
        result = register_webhook()
        self.assertTrue(result)
        mock_create.assert_called_once_with("test/repo", "https://example.com/webhook")

    @patch("src.webhook_registration._update_hook")
    @patch("src.webhook_registration._webhook_exists", return_value=456)
    @patch("src.webhook_registration.Config")
    def test_updates_existing_webhook(
        self,
        mock_config: MagicMock,
        mock_exists: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        mock_config.APP_BASE_URL = "https://example.com"
        mock_config.GITHUB_TOKEN = "tok"
        mock_config.REPOSITORY_URL = "https://github.com/test/repo"
        mock_config.GITHUB_WEBHOOK_SECRET = "secret"
        mock_update.return_value = {"id": 456}
        result = register_webhook()
        self.assertTrue(result)
        mock_update.assert_called_once_with(
            "test/repo", 456, "https://example.com/webhook"
        )


class WebhookExistsTestCase(unittest.TestCase):
    @patch("src.webhook_registration._list_hooks")
    def test_finds_matching_hook(self, mock_list: MagicMock) -> None:
        mock_list.return_value = [
            {"id": 1, "config": {"url": "https://other.com/hook"}},
            {"id": 2, "config": {"url": "https://example.com/webhook"}},
        ]
        self.assertEqual(_webhook_exists("test/repo", "https://example.com/webhook"), 2)

    @patch("src.webhook_registration._list_hooks")
    def test_returns_none_when_no_match(self, mock_list: MagicMock) -> None:
        mock_list.return_value = [
            {"id": 1, "config": {"url": "https://other.com/hook"}},
        ]
        self.assertIsNone(_webhook_exists("test/repo", "https://example.com/webhook"))


if __name__ == "__main__":
    unittest.main()
