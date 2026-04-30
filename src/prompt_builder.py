"""Prompt builder for Devin remediation sessions.

PR-01 – PR-05: Builds a structured prompt containing repo URL, issue
number, title, body, and type-specific remediation instructions
following the Devin prompt templates cheat sheet.

See: https://docs.devin.ai/essential-guidelines/prompt-templates-cheat-sheet
"""

import os

# ---------------------------------------------------------------------------
# Type-specific prompt templates (based on Devin prompt cheat sheet)
# ---------------------------------------------------------------------------

_BUG_TEMPLATE = """\
Fix the bug described in issue #{issue_number} in the repository below.

Repository: {repo_url}
Branch: main
Issue: #{issue_number} — {issue_title}

Bug description:
{issue_body}

Please:
1. Investigate the root cause of the bug
2. Implement a fix that addresses the root cause — not just the symptom
3. Add a regression test to prevent this issue from recurring
4. Run the existing test suite to ensure no regressions
5. Open a pull request with:
   - Title: "fix: {issue_title} (closes #{issue_number})"
   - Body: explanation of root cause, what was changed, and why
   - Reference to Issue #{issue_number}

Scope: Do not make changes beyond what is required to fix this bug.\
"""

_FEATURE_TEMPLATE = """\
Implement the feature described in issue #{issue_number} in the repository below.

Repository: {repo_url}
Branch: main
Issue: #{issue_number} — {issue_title}

Feature requirements:
{issue_body}

Please:
1. Review the existing codebase for related patterns and conventions
2. Implement the feature following the project's existing conventions
3. Add input validation and error handling where appropriate
4. Write unit tests for the new functionality
5. Run the existing test suite to ensure no regressions
6. Update documentation if applicable
7. Open a pull request with:
   - Title: "feat: {issue_title} (closes #{issue_number})"
   - Body: explanation of the implementation approach and any design decisions
   - Reference to Issue #{issue_number}

Scope: Do not make changes beyond what is required to implement this feature.\
"""

_TASK_TEMPLATE = """\
Complete the task described in issue #{issue_number} in the repository below.

Repository: {repo_url}
Branch: main
Issue: #{issue_number} — {issue_title}

Task description:
{issue_body}

Please:
1. Analyse the current implementation and understand what needs to change
2. Implement the changes following the project's existing patterns and conventions
3. Keep all existing functionality intact
4. Ensure all existing tests still pass
5. Add tests for any new functions or changed behaviour
6. Open a pull request with:
   - Title: "chore: {issue_title} (closes #{issue_number})"
   - Body: explanation of what was changed and why
   - Reference to Issue #{issue_number}

Scope: Do not make changes beyond what is required to complete this task.\
"""

# Map GitHub issue types to their templates and conventional commit prefixes
_TYPE_CONFIG: dict[str, dict[str, str]] = {
    "bug": {"template": _BUG_TEMPLATE, "prefix": "fix"},
    "feature": {"template": _FEATURE_TEMPLATE, "prefix": "feat"},
    "task": {"template": _TASK_TEMPLATE, "prefix": "chore"},
}


def _get_type_config(issue_type: str) -> dict[str, str]:
    """Return template and prefix config for the given issue type."""
    return _TYPE_CONFIG.get(issue_type.lower(), _TYPE_CONFIG["task"])


def build_prompt(
    repo_url: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
    issue_type: str = "task",
) -> str:
    """Build a type-specific remediation prompt from issue context.

    Each issue type (bug, feature, task) uses a distinct prompt template
    modelled on the Devin prompt templates cheat sheet. The template
    is overridable via the PROMPT_TEMPLATE environment variable or a
    file path in PROMPT_TEMPLATE_FILE (PR-05).
    """
    # PR-05: Allow env-based override (applies to all types)
    template_file = os.environ.get("PROMPT_TEMPLATE_FILE")
    if template_file and os.path.isfile(template_file):
        with open(template_file, "r") as fh:
            template = fh.read()
    elif os.environ.get("PROMPT_TEMPLATE"):
        template = os.environ["PROMPT_TEMPLATE"]
    else:
        config = _get_type_config(issue_type)
        template = config["template"]

    return template.format(
        repo_url=repo_url,
        issue_number=issue_number,
        issue_title=issue_title,
        issue_body=issue_body,
        issue_type=issue_type,
    )
