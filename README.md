# Superset Issues Auto-Remediation

Event-driven issue remediation system that automatically detects GitHub issues labelled with configured types (`bug`, `feature`, `task`) and triggers [Devin AI](https://devin.ai) sessions to analyse, implement, and open pull requests.

## Architecture

```
GitHub Issue (labels: bug, feature, task)
        │ Webhook POST
        ▼
  Webhook Listener ──► Remediation Orchestrator ──► Devin API
        │                       │
        ▼                       ▼
    HTTP 200              SQLite Store
   (immediate)                  │
                                ▼
                        Operations Dashboard
```

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

## Configuration

All configuration is injected via environment variables:

| Variable | Description | Default | Required |
|---|---|---|---|
| `GITHUB_WEBHOOK_SECRET` | Shared secret for HMAC-SHA256 signature validation | — | Yes |
| `DEVIN_API_KEY` | Devin API authentication key | — | Yes |
| `GITHUB_TOKEN` | GitHub personal access token | — | No |
| `REPOSITORY_URL` | Target GitHub repository URL | — | Yes |
| `ISSUE_LABELS` | Comma-separated list of issue labels that trigger remediation | `bug,feature,task` | No |
| `POLLING_INTERVAL_SECONDS` | Devin session poll interval | `30` | No |
| `SESSION_TIMEOUT_MINUTES` | Max session duration before timeout | `45` | No |
| `DATABASE_PATH` | SQLite database file path | `/data/sessions.db` | No |
| `DASHBOARD_PORT` | Dashboard HTTP port | `5000` | No |

## Supported Issue Types

The system supports all standard GitHub issue types:

| Label | PR Prefix | Description |
|---|---|---|
| `bug` | `fix:` | Bug fixes and error corrections |
| `feature` | `feat:` | New features and enhancements |
| `task` | `chore:` | Maintenance tasks, dependency updates, refactoring |

Labels are configurable via the `ISSUE_LABELS` environment variable (comma-separated).

## How It Works

1. **Webhook received** — GitHub sends a POST when an issue is created or labelled
2. **Signature validated** — HMAC-SHA256 verification ensures the payload is authentic
3. **Label matched** — Only issues with at least one configured label proceed
4. **Idempotency check** — Duplicate issues are detected and skipped
5. **Devin session created** — A structured prompt with issue context and type is sent to the Devin API
6. **Session polled** — The orchestrator polls session status until completion, failure, or timeout
7. **Result recorded** — PR URL, status, and timing metrics are persisted to SQLite
8. **Dashboard updated** — Real-time view of all remediation sessions

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Lint** — `ruff check` and `ruff format --check` on all Python files
- **Test** — `pytest` runs all 26 tests
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
- **Session list** with issue numbers, titles, statuses, and clickable PR links
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
| Session manager | Python + requests |
| Observability store | SQLite |
| Dashboard | Flask + Jinja2 |
| Containerisation | Docker + docker-compose |
| CI | GitHub Actions |
