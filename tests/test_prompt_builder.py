"""Tests for prompt builder."""

import os
import unittest

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")

from src.prompt_builder import build_prompt


class PromptBuilderTestCase(unittest.TestCase):
    def test_default_prompt_contains_all_fields(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=42,
            issue_title="XSS in search",
            issue_body="The search bar is vulnerable to XSS.",
        )
        self.assertIn("https://github.com/org/repo", prompt)
        self.assertIn("#42", prompt)
        self.assertIn("XSS in search", prompt)
        self.assertIn("The search bar is vulnerable to XSS.", prompt)
        self.assertIn("pull request", prompt)
        self.assertIn("unit tests", prompt)

    def test_custom_template_via_env(self) -> None:
        os.environ["PROMPT_TEMPLATE"] = "Fix {issue_title} in {repo_url}"
        try:
            prompt = build_prompt(
                repo_url="https://github.com/org/repo",
                issue_number=1,
                issue_title="Bug",
                issue_body="body",
            )
            self.assertEqual(prompt, "Fix Bug in https://github.com/org/repo")
        finally:
            del os.environ["PROMPT_TEMPLATE"]


if __name__ == "__main__":
    unittest.main()
