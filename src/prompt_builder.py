"""Prompt builder for Devin remediation sessions.

PR-01 – PR-05: Builds a structured prompt containing repo URL, issue
number, title, body, and scoped remediation instructions.
"""

import os

DEFAULT_PROMPT_TEMPLATE = """\
You are remediating a security vulnerability in the following repository.

Repository: {repo_url}
Branch: main
Issue: #{issue_number} — {issue_title}

Description:
{issue_body}

Instructions:
1. Analyse the vulnerability described above
2. Identify the specific file(s) and line(s) affected
3. Implement a fix that addresses the root cause — not just the symptom
4. Write or update unit tests covering the vulnerability scenario
5. Ensure all existing tests continue to pass
6. Open a pull request with:
   - Title: "fix: remediate {issue_title} (closes #{issue_number})"
   - Body: explanation of what was vulnerable and how you fixed it
   - Reference to Issue #{issue_number}

Scope: Do not make changes beyond what is required to remediate this specific issue.\
"""


def build_prompt(
    repo_url: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
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

    return template.format(
        repo_url=repo_url,
        issue_number=issue_number,
        issue_title=issue_title,
        issue_body=issue_body,
    )
