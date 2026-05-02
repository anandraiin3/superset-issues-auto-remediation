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

## Quick Start (Podman)

Uses the **same `.env` file** as the main remediation app — no separate configuration needed.

### 1. Build the container image

```bash
podman build -t issue-generator tests/issue-generator/
```

### 2. Create test issues

```bash
# Create 5 random issues (mount file so removals persist)
podman run --env-file .env \
  -v $(pwd)/tests/issue-generator/issues.md:/app/issues.md \
  issue-generator --batch 5
```

> **Important:** Mount `issues.md` with `-v` so created issues are removed from the file and won't repeat on the next run. Without `-v`, each container starts from the original 50-issue pool.

### More examples

```bash
# Create all remaining issues
podman run --env-file .env \
  -v $(pwd)/tests/issue-generator/issues.md:/app/issues.md \
  issue-generator

# Dry run — parse and print issues without creating them
podman run --env-file .env issue-generator --dry-run

# Custom delay between API calls (default: 2 seconds)
podman run --env-file .env \
  -v $(pwd)/tests/issue-generator/issues.md:/app/issues.md \
  issue-generator --batch 10 --delay 5

# Create a single random issue
podman run --env-file .env \
  -v $(pwd)/tests/issue-generator/issues.md:/app/issues.md \
  issue-generator --batch 1
```

## Without Container

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
2. **Randomly selects** issues from the pool (not sequential)
3. Creates each issue on the target repo via the GitHub API with the `[Type]` title prefix
4. Removes the created issue from `issues.md` after successful creation
5. Updates the total count in the file header

The markdown file acts as a shrinking work queue — re-running the container picks up where you left off. Each run picks different random issues from the remaining pool.
