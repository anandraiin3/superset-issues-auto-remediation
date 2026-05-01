"""Tests for prompt builder."""

import os
import unittest

os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DEVIN_API_KEY", "test-key")
os.environ.setdefault("DEVIN_ORG_ID", "test-org")
os.environ.setdefault("REPOSITORY_URL", "https://github.com/test/repo")

from src.prompt_builder import build_prompt


class PromptBuilderTestCase(unittest.TestCase):
    # -- Bug type ----------------------------------------------------------

    def test_bug_prompt_uses_fix_prefix(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=42,
            issue_title="XSS in search",
            issue_body="The search bar is vulnerable to XSS.",
            issue_type="bug",
        )
        self.assertIn("fix:", prompt)

    def test_bug_prompt_follows_cheat_sheet_structure(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=42,
            issue_title="Crash on save",
            issue_body="App crashes when saving.",
            issue_type="bug",
        )
        self.assertIn("Fix the bug", prompt)
        self.assertIn("Investigate the root cause", prompt)
        self.assertIn("regression test", prompt)
        self.assertIn("Bug description:", prompt)
        self.assertIn("#42", prompt)
        self.assertIn("https://github.com/org/repo", prompt)
        self.assertIn("App crashes when saving.", prompt)

    # -- Feature type ------------------------------------------------------

    def test_feature_prompt_uses_feat_prefix(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=10,
            issue_title="Add dark mode",
            issue_body="Support dark mode.",
            issue_type="feature",
        )
        self.assertIn("feat:", prompt)

    def test_feature_prompt_follows_cheat_sheet_structure(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=10,
            issue_title="Add search",
            issue_body="Implement search functionality.",
            issue_type="feature",
        )
        self.assertIn("Implement the feature", prompt)
        self.assertIn("Feature requirements:", prompt)
        self.assertIn("existing conventions", prompt)
        self.assertIn("input validation", prompt)
        self.assertIn("unit tests", prompt)

    # -- Task type ---------------------------------------------------------

    def test_task_prompt_uses_chore_prefix(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=11,
            issue_title="Update deps",
            issue_body="Upgrade packages.",
            issue_type="task",
        )
        self.assertIn("chore:", prompt)

    def test_task_prompt_follows_cheat_sheet_structure(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=11,
            issue_title="Refactor config",
            issue_body="Clean up config module.",
            issue_type="task",
        )
        self.assertIn("Complete the task", prompt)
        self.assertIn("Task description:", prompt)
        self.assertIn("existing patterns", prompt)
        self.assertIn("existing functionality intact", prompt)

    # -- Default and override ----------------------------------------------

    def test_default_type_is_task(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=13,
            issue_title="Something",
            issue_body="body",
        )
        self.assertIn("Complete the task", prompt)
        self.assertIn("chore:", prompt)

    def test_unknown_type_falls_back_to_task(self) -> None:
        prompt = build_prompt(
            repo_url="https://github.com/org/repo",
            issue_number=14,
            issue_title="Custom type",
            issue_body="body",
            issue_type="epic",
        )
        self.assertIn("Complete the task", prompt)
        self.assertIn("chore:", prompt)

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

    def test_each_type_produces_distinct_prompt(self) -> None:
        args = {
            "repo_url": "https://github.com/org/repo",
            "issue_number": 99,
            "issue_title": "Test",
            "issue_body": "body",
        }
        bug = build_prompt(**args, issue_type="bug")
        feat = build_prompt(**args, issue_type="feature")
        task = build_prompt(**args, issue_type="task")
        self.assertNotEqual(bug, feat)
        self.assertNotEqual(feat, task)
        self.assertNotEqual(bug, task)


if __name__ == "__main__":
    unittest.main()
