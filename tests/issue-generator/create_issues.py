"""Issue generator — reads issues.md and creates them on the target GitHub repo.

Reads environment variables from the same .env file used by the main
remediation app.  After each issue is successfully created, it is removed
from issues.md so the file acts as a shrinking work queue.

Usage:
    python create_issues.py [--batch N] [--delay SECONDS] [--dry-run]

Environment variables (same .env as the remediation app):
    GITHUB_TOKEN       — GitHub PAT with Issues: Read & Write permission
    REPOSITORY_URL     — Target repo (e.g. https://github.com/anandraiin3/superset)
"""

import argparse
import os
import random
import re
import sys
import time

import requests

ISSUES_FILE = os.path.join(os.path.dirname(__file__), "issues.md")
VALID_TYPES = {"Bug", "Feature", "Task"}


def _extract_owner_repo(repo_url: str) -> str:
    """Extract 'owner/repo' from a GitHub URL."""
    match = re.search(r"github\.com/([^/]+/[^/\s\"']+)", repo_url)
    if not match:
        print(f"ERROR: Cannot parse REPOSITORY_URL: {repo_url}", file=sys.stderr)
        sys.exit(1)
    return match.group(1).rstrip("/")


def _parse_issues(filepath: str) -> list[dict]:
    """Parse issues.md into a list of issue dicts.

    Splits on ### [Type] Title headings.  Internal --- separators within
    issue bodies are preserved.
    """
    with open(filepath) as f:
        content = f.read()

    # Split into blocks at each ### [Type] heading
    heading_pattern = re.compile(r"^### \[(Bug|Feature|Task)\] (.+?)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(content))

    issues = []
    for i, m in enumerate(matches):
        issue_type = m.group(1)
        title = m.group(2).strip()

        # Block runs from after the heading to the next heading (or EOF)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end].strip()

        # Strip trailing section header (for last issue in a section)
        block = re.sub(r"\n## (?:Bug|Feature|Task)\s*$", "", block)
        # Strip trailing --- separator between issues
        block = re.sub(r"\n---\s*$", "", block)

        # Extract source URL
        source_match = re.search(r"\*\*Source:\*\* \[.*?\]\((.*?)\)", block)
        source_url = source_match.group(1) if source_match else ""

        # Extract body (everything after the **Type:** line)
        body_match = re.search(r"\*\*Type:\*\* \w+\s*\n(.*)", block, re.DOTALL)
        body = body_match.group(1).strip() if body_match else ""

        # raw_block = full text from heading to next heading (for removal).
        # Trim before any ## section headers so removing the last issue
        # of a section doesn't destroy the next section header.
        raw_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        raw_block = content[m.start() : raw_end]
        section_hdr = re.search(r"\n## (?:Bug|Feature|Task)\s*\n", raw_block)
        if section_hdr:
            raw_block = raw_block[: section_hdr.start()]

        issues.append(
            {
                "type": issue_type,
                "title": title,
                "body": body,
                "source_url": source_url,
                "raw_match": raw_block,
            }
        )

    return issues


def _create_github_issue(
    owner_repo: str, title: str, body: str, issue_type: str, source_url: str, token: str
) -> int:
    """Create an issue on GitHub. Returns the issue number."""
    # Prefix title with type for clarity
    prefixed_title = f"[{issue_type}] {title}"

    # Add attribution to body
    full_body = body
    if source_url:
        full_body += f"\n\n---\n_Sourced from: {source_url}_"

    resp = requests.post(
        f"https://api.github.com/repos/{owner_repo}/issues",
        json={"title": prefixed_title, "body": full_body},
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["number"]


def _remove_issue_from_file(filepath: str, raw_match: str) -> None:
    """Remove a created issue block (and its trailing ---) from the markdown."""
    with open(filepath) as f:
        content = f.read()

    # Remove the full issue block (heading through to next heading)
    content = content.replace(raw_match, "", 1)

    # Clean up multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    with open(filepath, "w") as f:
        f.write(content)


def _update_counts(filepath: str) -> None:
    """Update the Total line at the top of the markdown file."""
    with open(filepath) as f:
        content = f.read()

    counts = {
        t: len(re.findall(rf"^### \[{t}\]", content, re.MULTILINE)) for t in VALID_TYPES
    }
    total = sum(counts.values())
    new_total_line = (
        f"**Total: {total} issues** "
        f"(Bug: {counts['Bug']}, Feature: {counts['Feature']}, Task: {counts['Task']})"
    )
    content = re.sub(r"\*\*Total: \d+ issues\*\*.*", new_total_line, content)

    with open(filepath, "w") as f:
        f.write(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create GitHub issues from issues.md")
    parser.add_argument(
        "--batch", type=int, default=0, help="Max issues to create (0 = all)"
    )
    parser.add_argument(
        "--delay", type=float, default=2.0, help="Seconds between API calls"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse and print without creating"
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "").strip().strip('"').strip("'")
    repo_url = os.environ.get("REPOSITORY_URL", "").strip().strip('"').strip("'")

    if not token:
        print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    if not repo_url:
        print("ERROR: REPOSITORY_URL not set", file=sys.stderr)
        sys.exit(1)

    owner_repo = _extract_owner_repo(repo_url)
    issues = _parse_issues(ISSUES_FILE)

    if not issues:
        print("No issues found in issues.md — nothing to create.")
        return

    limit = args.batch if args.batch > 0 else len(issues)
    selected = random.sample(issues, min(limit, len(issues)))
    print(
        f"Found {len(issues)} issues. Randomly selected {len(selected)} to create on {owner_repo}..."
    )
    print()

    created = 0
    for issue in selected:
        print(f"  [{issue['type']}] {issue['title'][:80]}", end=" ... ")

        if args.dry_run:
            print("(dry run — skipped)")
            created += 1
            continue

        try:
            num = _create_github_issue(
                owner_repo,
                issue["title"],
                issue["body"],
                issue["type"],
                issue["source_url"],
                token,
            )
            print(f"created #{num}")
            _remove_issue_from_file(ISSUES_FILE, issue["raw_match"])
            _update_counts(ISSUES_FILE)
            created += 1
        except requests.HTTPError as exc:
            print(f"FAILED: {exc}")
            if exc.response is not None:
                print(f"    Response: {exc.response.text[:200]}")
            continue

        if created < limit:
            time.sleep(args.delay)

    print()
    print(f"Done. Created {created}/{limit} issues on {owner_repo}.")
    remaining = _parse_issues(ISSUES_FILE)
    print(f"Remaining in issues.md: {len(remaining)}")


if __name__ == "__main__":
    main()
