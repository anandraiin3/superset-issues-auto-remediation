# Superset Issues Auto-Remediation

Event-driven issue remediation system that automatically detects GitHub issues by their native **issue type** (`Bug`, `Feature`, `Task`) and triggers [Devin AI](https://devin.ai) sessions to analyse, implement, and open pull requests.

## Architecture

```
GitHub Issue (type: Bug / Feature / Task)
        │ Webhook POST
        ▼
  Webhook Listener ──► Remediation Orchestrator ──► Devin API v3
        │                       │                       │
        ▼                       ▼                       ▼
    HTTP 200              SQLite Store          Devin Messages API
   (immediate)                  │                       │
                                ▼                       ▼
                        Operations Dashboard    Auto-Comment on
                        (granular status)       GitHub Issue
```

See [`docs/prd_v1.md`](docs/prd_v1.md) for full architecture, [workflow diagram](docs/workflow-diagram.png), and [state lifecycle](docs/state-lifecycle.png).

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/anandraiin3/superset-issues-auto-remediation.git
cd superset-issues-auto-remediation
cp .env.example .env
# Edit .env with your actual keys
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

The system is now:
- Listening for webhooks on **port 5000** at `/webhook`
- Serving the dashboard at `/dashboard`
- Responding to health checks at `/health`

### 3. Configure GitHub Webhook

1. Go to your GitHub repository **Settings → Webhooks → Add webhook**
2. Set **Payload URL** to `https://your-server:5000/webhook`
3. Set **Content type** to `application/json`
4. Set **Secret** to match your `GITHUB_WEBHOOK_SECRET`
5. Select **Let me select individual events** → check **Issues**
6. Save

### 4. Enable Issue Types

Issue types (`Bug`, `Feature`, `Task`) are a native GitHub feature. To enable them:
1. Go to your **Organization Settings → Issue Types**
2. Ensure the desired types are enabled

## Configuration

All configuration is injected via environment variables:

| Variable | Description | Default | Required |
|---|---|---|---|
| `GITHUB_WEBHOOK_SECRET` | Shared secret for HMAC-SHA256 signature validation | — | Yes |
| `DEVIN_API_KEY` | Devin API key (service user, `cog_` prefix) | — | Yes |
| `DEVIN_ORG_ID` | Devin organisation ID (Settings → Service Users) | — | Yes |
| `GITHUB_TOKEN` | GitHub personal access token | — | No |
| `REPOSITORY_URL` | Target GitHub repository URL | — | Yes |
| `ISSUE_TYPES` | Comma-separated list of GitHub issue types that trigger remediation | `bug,feature,task` | No |
| `POLLING_INTERVAL_SECONDS` | Devin session poll interval | `30` | No |
| `SESSION_TIMEOUT_MINUTES` | Max session duration before timeout | `45` | No |
| `DATABASE_PATH` | SQLite database file path | `/data/sessions.db` | No |
| `DASHBOARD_PORT` | Dashboard HTTP port | `5000` | No |

## Supported Issue Types

The system uses GitHub's native [issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization) (not labels) to classify and process issues:

| Issue Type | PR Prefix | Description |
|---|---|---|
| `Bug` | `fix:` | Bug fixes and error corrections |
| `Feature` | `feat:` | New features and enhancements |
| `Task` | `chore:` | Maintenance tasks, dependency updates, refactoring |

The webhook reads the `issue.type.name` field from the GitHub webhook payload. Issues without a type or with an unsupported type are skipped.

## How It Works

1. **Webhook received** — GitHub sends a POST when an issue is created or labelled
2. **Signature validated** — HMAC-SHA256 verification ensures the payload is authentic
3. **Issue type checked** — Only issues whose `type.name` matches a configured type proceed
4. **Idempotency check** — Duplicate issues are detected and skipped
5. **Devin session created** — A structured prompt with issue context and type is sent to the Devin API v3
6. **Session polled** — The orchestrator polls session status until completion, failure, or timeout
   - **Granular tracking**: `working` → `pr_ready` (when PR detected) → `waiting_for_user` → `completed`
   - **Auto-comment**: When Devin asks an issue-related question, it's posted back to the GitHub issue
   - Infrastructure questions (permissions, tokens) are filtered out and NOT posted
7. **Result recorded** — PR URL, status detail, and timing metrics are persisted to SQLite
8. **Dashboard updated** — Real-time view with granular status and Devin session links

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Lint** — `ruff check` and `ruff format --check` on all Python files
- **Test** — `pytest` runs all tests
- **Docker build** — Verifies the Docker image builds successfully

CI runs on every push to `main` and on all pull requests.

## Development

### Run locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Export required env vars
export GITHUB_WEBHOOK_SECRET=your_secret
export DEVIN_API_KEY=your_key
export DEVIN_ORG_ID=your_org_id
export REPOSITORY_URL=https://github.com/your/repo
export DATABASE_PATH=./data/sessions.db

python app.py
```

### Run tests

```bash
pip install -r requirements.txt pytest
python -m pytest tests/ -v
```

### Lint

```bash
pip install ruff
ruff check src/ tests/ app.py
ruff format --check src/ tests/ app.py
```

## Dashboard

Access the operations dashboard at `/dashboard` to see:

- **Session counts** by status (active, completed, failed)
- **Success rate** percentage
- **Average time-to-remediation**
- **Session list** with issue numbers, titles, statuses, status details, clickable PR links, and Devin session links
- **Granular status detail** — colour-coded sub-states: `working` (green), `waiting for user` (amber), `pr_ready` (blue)
- **Status filters** to focus on specific session states

The dashboard auto-refreshes every 30 seconds.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/webhook` | POST | GitHub webhook receiver |
| `/dashboard` | GET | Operations dashboard |
| `/health` | GET | Health check |

## Tech Stack

| Component | Technology |
|---|---|
| Webhook listener | Python + Flask |
| Async processing | Python threading |
| Session manager | Python + requests (Devin API v3) |
| Observability store | SQLite |
| Dashboard | Flask + Jinja2 |
| Containerisation | Docker + docker-compose |
| CI | GitHub Actions |
