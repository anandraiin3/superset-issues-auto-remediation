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
```

Edit `.env` with your actual credentials (see [Credentials Setup](#credentials-setup) below for details on each key):

```env
# Required
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
DEVIN_API_KEY=cog_your_devin_service_user_key
DEVIN_ORG_ID=your_devin_org_id
GITHUB_TOKEN=ghp_your_github_personal_access_token
REPOSITORY_URL=https://github.com/your-org/your-repo

# Optional — set to auto-register webhook on startup
APP_BASE_URL=https://your-server.example.com

# Optional — defaults shown
ISSUE_TYPES=bug,feature,task
POLLING_INTERVAL_SECONDS=30
SESSION_TIMEOUT_MINUTES=45
DATABASE_PATH=/data/sessions.db
DASHBOARD_PORT=5000
```

### 2. Run with Docker Compose (recommended)

```bash
docker-compose up --build
```

This builds the image and starts the container with:
- Webhook listener on **port 5000** at `/webhook`
- Operations dashboard at `/dashboard`
- Health check at `/health`
- Persistent SQLite storage via a Docker volume (`session-data:/data`)
- Auto-restart on failure (`unless-stopped` policy)

### 3. Run with Docker (standalone)

If you prefer running the Docker container directly without Compose:

```bash
# Build the image
docker build -t superset-remediation .

# Run the container
docker run -d \
  --name superset-remediation \
  -p 5000:5000 \
  -v superset-session-data:/data \
  -e GITHUB_WEBHOOK_SECRET="your_webhook_secret" \
  -e DEVIN_API_KEY="cog_your_devin_service_user_key" \
  -e DEVIN_ORG_ID="your_devin_org_id" \
  -e GITHUB_TOKEN="ghp_your_github_token" \
  -e REPOSITORY_URL="https://github.com/your-org/your-repo" \
  -e ISSUE_TYPES="bug,feature,task" \
  -e POLLING_INTERVAL_SECONDS=30 \
  -e SESSION_TIMEOUT_MINUTES=45 \
  -e DATABASE_PATH=/data/sessions.db \
  superset-remediation
```

Alternatively, pass all env vars from a file:

```bash
docker run -d \
  --name superset-remediation \
  -p 5000:5000 \
  -v superset-session-data:/data \
  --env-file .env \
  superset-remediation
```

### 4. Configure GitHub Webhook

**Option A — Automatic registration (recommended):**

Set `APP_BASE_URL` in your `.env` to the public URL of your server:

```env
APP_BASE_URL=https://your-server.example.com
```

On startup, the app will automatically register a webhook on the repository specified in `REPOSITORY_URL`. If a matching webhook already exists, it updates the config. If `APP_BASE_URL` is not set, auto-registration is skipped.

> Requires `GITHUB_TOKEN` with **Webhooks: Read & Write** permission.

**Option B — Manual registration:**

1. Go to your GitHub repository **Settings → Webhooks → Add webhook**
2. Set **Payload URL** to `https://your-server:5000/webhook`
3. Set **Content type** to `application/json`
4. Set **Secret** to match your `GITHUB_WEBHOOK_SECRET`
5. Select **Let me select individual events** → check **Issues**
6. Save

> **Note:** The server must be publicly reachable for GitHub to deliver webhooks. Use a reverse proxy (nginx, Caddy) or a tunnel (ngrok, Cloudflare Tunnel) if running behind NAT.

### 5. Enable Issue Types

Issue types (`Bug`, `Feature`, `Task`) are a native GitHub feature. To enable them:
1. Go to your **Organization Settings → Issue Types**
2. Ensure the desired types are enabled

---

## Credentials Setup

### Devin API Key (`DEVIN_API_KEY`)

A **service user API key** with `cog_` prefix is required.

1. Go to [app.devin.ai/settings](https://app.devin.ai/settings) → **Service Users**
2. Create a service user (or use an existing one)
3. Generate an API key — it will start with `cog_`
4. **Required permission:** `ManageOrgSessions` (to create, retrieve, and list sessions)

> Legacy keys with `apk_` prefix will **not** work with the v3 API.

### Devin Organisation ID (`DEVIN_ORG_ID`)

1. Go to [app.devin.ai/settings](https://app.devin.ai/settings) → **Service Users**
2. Your org ID is displayed on the page (e.g., `org-abc123def456`)

### GitHub Token (`GITHUB_TOKEN`)

A GitHub personal access token is used to post auto-comments on issues when Devin has questions.

**Required permissions** (for the target repository):

| Permission | Scope | Why |
|---|---|---|
| **Issues** | Read & Write | Post Devin’s questions as comments on issues |
| **Webhooks** | Read & Write | Required for automatic webhook registration (when `APP_BASE_URL` is set) |
| **Contents** | Read | Devin needs to read repo contents for remediation |

**Option A — Fine-grained PAT** (recommended):
1. Go to [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
2. Select the target repository (e.g., `your-org/your-repo`)
3. Under **Repository permissions**, enable:
   - Issues: **Read and write**
   - Webhooks: **Read and write** (if you want the app to manage webhooks)
   - Contents: **Read-only**
4. Generate and copy the token

**Option B — Classic PAT:**
1. Go to [github.com/settings/tokens/new?scopes=repo,admin:repo_hook](https://github.com/settings/tokens/new?scopes=repo,admin:repo_hook)
2. Select `repo` and `admin:repo_hook` scopes
3. Generate and copy the token

### GitHub Webhook Secret (`GITHUB_WEBHOOK_SECRET`)

A shared secret string used to validate webhook payloads via HMAC-SHA256. Choose any random string:

```bash
# Generate a random secret
openssl rand -hex 32
```

Use the same value in your `.env` file and when configuring the webhook in GitHub (step 4 above).

### Repository URL (`REPOSITORY_URL`)

The full HTTPS URL of the GitHub repository to monitor for issues:

```
https://github.com/your-org/your-repo
```

This is used to construct issue links, PR links, and context for Devin sessions.

## Configuration

All configuration is injected via environment variables:

| Variable | Description | Default | Required |
|---|---|---|---|
| `GITHUB_WEBHOOK_SECRET` | Shared secret for HMAC-SHA256 signature validation | — | Yes |
| `DEVIN_API_KEY` | Devin API key (service user, `cog_` prefix) | — | Yes |
| `DEVIN_ORG_ID` | Devin organisation ID (Settings → Service Users) | — | Yes |
| `GITHUB_TOKEN` | GitHub personal access token (see [Credentials Setup](#credentials-setup)) | — | Yes (for auto-comments) |
| `REPOSITORY_URL` | Target GitHub repository URL | — | Yes |
| `APP_BASE_URL` | Public base URL of this app (enables automatic webhook registration on startup) | — | No |
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
7. **Result recorded** — PR URL, status detail, ACU cost, and timing metrics are persisted to SQLite
8. **Dashboard updated** — Real-time view with clickable issue/PR/session links, granular status, and cost tracking

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

## Remediation Operations Dashboard

Access the dashboard at `/dashboard` to see:

- **Key metrics** — session counts, success rate, average overall time (ms), total cost (ACUs)
- **Session table** — each row shows issue (linked to GitHub), status badge + sub-state, action links (PR + Devin session), cost, timing (Overall ms, Devin ms), and created timestamp
- **Status filters** — filter by created, running, completed, failed, timed out
- **Granular status detail** — colour-coded sub-states: `working` (green), `waiting for user` (amber), `pr_ready` (blue)
- **Cost tracking** — per-session ACU consumption and total cost across all sessions
- **Duration tracking** — Overall (webhook → PR) and Devin (session creation → exit) in milliseconds
- **Live indicator** — auto-refreshes every 30 seconds with a pulse dot

The UI follows [Figma's 7 UI design principles](https://www.figma.com/resource-library/ui-design-principles/) and [16 practical UI tips](https://github.com/johndelatto/step-by-step-ui-design-case-study-to-quickly-fix-an-example-user-interface-using-ui-design-tips): design tokens, WCAG AA contrast, responsive layout, visual hierarchy, and keyboard accessibility.

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
