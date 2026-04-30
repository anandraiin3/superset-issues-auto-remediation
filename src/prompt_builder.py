"""Prompt builder for Devin remediation sessions.

PR-01 – PR-05: Builds a structured prompt containing repo URL, issue
number, title, body, issue type, and scoped remediation instructions.
"""

import os

DEFAULT_PROMPT_TEMPLATE = """\
You are resolving a GitHub issue in the following repository.

Repository: {repo_url}
Branch: main
Issue: #{issue_number} — {issue_title}
Issue Type: {issue_type}

Description:
{issue_body}

Instructions:
1. Analyse the issue described above
2. Identify the specific file(s) and line(s) affected
3. Implement a solution that addresses the root cause — not just the symptom
4. Write or update unit tests covering the changes
5. Ensure all existing tests continue to pass
6. Open a pull request with:
   - Title: "{pr_prefix}: {issue_title} (closes #{issue_number})"
   - Body: explanation of what was changed and why
   - Reference to Issue #{issue_number}

Scope: Do not make changes beyond what is required to resolve this specific issue.\
"""

# Map GitHub issue types to conventional commit prefixes
_TYPE_TO_PREFIX = {
    "bug": "fix",
    "feature": "feat",
    "task": "chore",
}


def _derive_pr_prefix(issue_type: str) -> str:
    """Map a GitHub issue type to a conventional commit prefix."""
    return _TYPE_TO_PREFIX.get(issue_type.lower(), "fix")


def build_prompt(
    repo_url: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
    issue_type: str = "task",
) -> str:
    """Build the remediation prompt from issue context.

    PR-05: The template is overridable via the PROMPT_TEMPLATE environment
    variable or a file path in PROMPT_TEMPLATE_FILE.
    """
    template = DEFAULT_PROMPT_TEMPLATE

    template_file = os.environ.get("PROMPT_TEMPLATE_FILE")
    if template_file and os.path.isfile(template_file):
        with open(template_file, "r") as fh:
            template = fh.read()
    elif os.environ.get("PROMPT_TEMPLATE"):
        template = os.environ["PROMPT_TEMPLATE"]

    pr_prefix = _derive_pr_prefix(issue_type)

    return template.format(
        repo_url=repo_url,
        issue_number=issue_number,
        issue_title=issue_title,
        issue_body=issue_body,
        issue_type=issue_type,
        pr_prefix=pr_prefix,
    )
