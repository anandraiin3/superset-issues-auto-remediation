# Issue Generator

Test tool that creates GitHub issues on the target repository from a curated list of real Apache Superset issues. Designed to trigger the remediation app's webhook and validate the full end-to-end flow.

## Issues

`issues.md` contains 50 issues sourced from [apache/superset](https://github.com/apache/superset):

| Type | Count | Description |
|------|-------|-------------|
| Bug | 16 | UI cosmetic issues, CSS fixes, display bugs |
| Feature | 17 | Enhancement requests, UI improvements |
| Task | 17 | Documentation, config, minor improvements |

All issues are intentionally simple (typos, CSS, labels, tooltips, etc.) to keep Devin session costs low.

## Usage

### With Docker/Podman (recommended)

Uses the **same `.env` file** as the main remediation app:

```bash
# Build the container
podman build -t issue-generator tests/issue-generator/

# Create all 50 issues (uses .env from the remediation app)
podman run --env-file .env issue-generator

# Create 5 issues at a time
podman run --env-file .env issue-generator --batch 5

# Dry run (parse and print without creating)
podman run --env-file .env issue-generator --dry-run

# Custom delay between API calls (default: 2 seconds)
podman run --env-file .env issue-generator --batch 10 --delay 5
```

**Important:** To persist the removal of created issues from `issues.md`, mount the file:

```bash
podman run --env-file .env \
  -v $(pwd)/tests/issue-generator/issues.md:/app/issues.md \
  issue-generator --batch 5
```

### Without Docker

```bash
pip install -r tests/issue-generator/requirements.txt

# Set env vars (or source .env)
export GITHUB_TOKEN="your_token"
export REPOSITORY_URL="https://github.com/anandraiin3/superset"

python tests/issue-generator/create_issues.py --batch 5
```

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub PAT with **Issues: Read & Write** permission on the target repo |
| `REPOSITORY_URL` | Target repo URL (e.g. `https://github.com/anandraiin3/superset`) |

These are the same variables used by the main remediation app, so you can reuse your existing `.env` file.

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--batch N` | `0` (all) | Max number of issues to create |
| `--delay SECONDS` | `2.0` | Pause between GitHub API calls |
| `--dry-run` | off | Parse and print issues without creating them |

## How It Works

1. Parses `issues.md` for issue blocks (format: `### [Type] Title`)
2. Creates each issue on the target repo via the GitHub API
3. Removes the created issue from `issues.md` after successful creation
4. Updates the total count in the file header

The markdown file acts as a shrinking work queue — re-running the container picks up where you left off.
