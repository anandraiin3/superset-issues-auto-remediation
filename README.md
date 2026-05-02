# Autonomous Issue Remediation Engine

Event-driven issue remediation system that automatically detects GitHub issues by type (`Bug`, `Feature`, `Task`) and triggers [Devin AI](https://devin.ai) sessions to analyse, implement, and open pull requests — fully autonomous, zero human intervention.

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

See [`docs/prd_v1.md`](docs/prd_v1.md) for full architecture, [executive overview](docs/executive-overview.mmd), and [state lifecycle](docs/state-lifecycle.mmd).

---

## Quick Start (Podman + ngrok)

This is the recommended local setup using **Podman** for container management and **ngrok** to expose the app to GitHub webhooks.

### 1. Clone and configure

```bash
git clone https://github.com/anandraiin3/Autonomous-Issue-Remediation-Engine.git
cd Autonomous-Issue-Remediation-Engine
cp .env.example .env
```

Edit `.env` with your credentials (see [Credentials Setup](#credentials-setup) for details on each key):

```env
# Required
GITHUB_WEBHOOK_SECRET=<run: openssl rand -hex 32>
DEVIN_API_KEY=cog_your_devin_service_user_key
DEVIN_ORG_ID=your_devin_org_id
GITHUB_TOKEN=ghp_your_github_personal_access_token
REPOSITORY_URL=https://github.com/your-org/your-repo

# Optional — set to auto-register webhook on startup
APP_BASE_URL=https://your-ngrok-url.ngrok-free.app

# Optional — defaults shown
ISSUE_TYPES=bug,feature,task
POLLING_INTERVAL_SECONDS=30
SESSION_TIMEOUT_MINUTES=45
DATABASE_PATH=/data/sessions.db
DASHBOARD_PORT=5000
```

### 2. Build the container image

```bash
podman build -t superset-remediation .
```

### 3. Start the app

```bash
podman run --rm \
  -p 5000:5000 \
  -v superset-session-data:/data \
  --env-file .env \
  superset-remediation
```

This starts:
- Webhook listener on **port 5000** at `/webhook`
- Operations dashboard at `/dashboard`
- Health check at `/health`
- Persistent SQLite storage via a Podman volume (`superset-session-data:/data`)

> **Tip:** If you changed `DASHBOARD_PORT` in `.env` (e.g. `DASHBOARD_PORT=5010`), update the `-p` flag to match: `-p 5010:5010`.

### 4. Expose with ngrok

In a separate terminal, expose your local app to the internet:

```bash
ngrok http 5000
```

Copy the public URL ngrok gives you (e.g. `https://abc123.ngrok-free.app`).

### 5. Configure the GitHub webhook

**Option A — Automatic registration (recommended):**

1. Stop the running container (`Ctrl+C`)
2. Update `APP_BASE_URL` in your `.env` to the ngrok URL:
   ```env
   APP_BASE_URL=https://abc123.ngrok-free.app
   ```
3. Restart the container:
   ```bash
   podman run --rm \
     -p 5000:5000 \
     -v superset-session-data:/data \
     --env-file .env \
     superset-remediation
   ```
4. The app auto-registers a webhook at `https://abc123.ngrok-free.app/webhook` on your repo. Check the logs for:
   ```
   webhook_registered — Webhook registered on your-org/your-repo (id=...)
   ```

> Requires `GITHUB_TOKEN` with **Webhooks: Read & Write** permission.

**Option B — Manual registration:**

1. Go to your GitHub repository **Settings → Webhooks → Add webhook**
2. Set **Payload URL** to `https://abc123.ngrok-free.app/webhook`
3. Set **Content type** to `application/json`
4. Set **Secret** to the same value as your `GITHUB_WEBHOOK_SECRET`
5. Select **Let me select individual events** → check **Issues**
6. Save

### 6. Test the setup

Create an issue on your target repo with a type of `Bug`, `Feature`, or `Task` (or prefix the title with `[Bug]`, `[Feature]`, or `[Task]` on personal repos). Watch the app logs — you'll see the webhook received and a Devin session created.

Open `http://localhost:5000/dashboard` to see the session on the Remediation Operations Dashboard.

---

## Credentials Setup

### Devin API Key (`DEVIN_API_KEY`)

A **service user API key** with `cog_` prefix is required.

1. Go to [app.devin.ai/settings](https://app.devin.ai/settings) → **Service Users**
2. Create a service user (or use an existing one)
3. Generate an API key — it will start with `cog_`
4. **Required permission:** `ManageOrgSessions` (to create, retrieve, terminate, and list sessions)

> Legacy keys with `apk_` prefix will **not** work with the v3 API.

### Devin Organisation ID (`DEVIN_ORG_ID`)

1. Go to [app.devin.ai/settings](https://app.devin.ai/settings) → **Service Users**
2. Your org ID is displayed on the page (e.g., `org-abc123def456`)

### GitHub Token (`GITHUB_TOKEN`)

A GitHub personal access token is used to post auto-comments on issues when Devin has questions.

**Required permissions** (for the target repository):

| Permission | Scope | Why |
|---|---|---|
| **Issues** | Read & Write | Post Devin's questions as comments on issues |
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

A shared secret string used to validate webhook payloads via HMAC-SHA256. Generate one:

```bash
openssl rand -hex 32
```

Use the same value in your `.env` file and when configuring the webhook in GitHub (step 5 above).

### Repository URL (`REPOSITORY_URL`)

The full HTTPS URL of the GitHub repository to monitor for issues:

```
https://github.com/your-org/your-repo
```

This is used to construct issue links, PR links, and context for Devin sessions.

---

## Configuration

All configuration is injected via environment variables:

| Variable | Description | Default | Required |
|---|---|---|---|
| `GITHUB_WEBHOOK_SECRET` | Shared secret for HMAC-SHA256 signature validation | — | Yes |
| `DEVIN_API_KEY` | Devin API key (service user, `cog_` prefix) | — | Yes |
| `DEVIN_ORG_ID` | Devin organisation ID (Settings → Service Users) | — | Yes |
| `GITHUB_TOKEN` | GitHub personal access token (see [Credentials Setup](#credentials-setup)) | — | Yes (for auto-comments) |
| `REPOSITORY_URL` | Target GitHub repository URL | — | Yes |
| `APP_BASE_URL` | Public base URL of this app (enables auto webhook registration); use your ngrok URL here | — | No |
| `ISSUE_TYPES` | Comma-separated list of GitHub issue types that trigger remediation | `bug,feature,task` | No |
| `POLLING_INTERVAL_SECONDS` | Devin session poll interval | `30` | No |
| `SESSION_TIMEOUT_MINUTES` | Max session duration before timeout | `45` | No |
| `DATABASE_PATH` | SQLite database file path | `/data/sessions.db` | No |
| `DASHBOARD_PORT` | Dashboard HTTP port | `5000` | No |

---

## Supported Issue Types

The system uses GitHub's native [issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization) (not labels) to classify and process issues:

| Issue Type | PR Prefix | Description |
|---|---|---|
| `Bug` | `fix:` | Bug fixes and error corrections |
| `Feature` | `feat:` | New features and enhancements |
| `Task` | `chore:` | Maintenance tasks, dependency updates, refactoring |

**Type detection priority:**
1. **Native issue type** — reads `issue.type.name` from the webhook payload (available on organization repos)
2. **Title prefix fallback** — if no native type is set, extracts the type from a `[Bug]`, `[Feature]`, or `[Task]` prefix in the issue title (works on personal repos)

Issues without a detectable type or with an unsupported type are skipped.

---

## How It Works

1. **Webhook received** — GitHub sends a POST when an issue is created or labelled
2. **Signature validated** — HMAC-SHA256 verification ensures the payload is authentic
3. **Issue type checked** — Only issues whose type matches a configured type proceed (native `type.name` or `[Type]` title prefix)
4. **Duplicate detection** — Duplicate issues are detected and skipped (both by issue number and by normalised title matching across existing sessions; failed/timed-out sessions are excluded so retries work)
5. **Devin session created** — A structured prompt with issue context and type is sent to the Devin API v3
6. **Session polled** — The orchestrator polls session status until completion, failure, or timeout
   - **Granular tracking**: `working` → `pr_ready` (when PR detected) → `waiting_for_user` → `completed`
   - **Auto-comment**: When Devin asks an issue-related question, it's posted back to the GitHub issue
   - **Auto-close**: When a PR is created and the session goes idle, it's archived and marked completed
   - Infrastructure questions (permissions, tokens) are filtered out and NOT posted
7. **Result recorded** — PR URL, status detail, ACU cost, and timing metrics are persisted to SQLite
8. **Dashboard updated** — Real-time view with clickable issue/PR/session links, granular status, and cost tracking

---

## Remediation Operations Dashboard

Access the dashboard at `http://localhost:5000/dashboard` to see:

- **Key metrics** — session counts, success rate, average overall time (ms), total cost (ACUs)
- **Session table** — each row shows issue (linked to GitHub), status badge + sub-state, action links (PR + Devin session), cost, timing (Overall ms, Devin ms), and created timestamp
- **Status filters** — filter by created, running, completed, failed, timed out
- **Granular status detail** — colour-coded sub-states: `working` (green), `waiting for user` (amber), `pr_ready` (blue), `auto_closed_with_pr`, `suspended_with_pr`, `timed_out_with_pr`
- **Cost tracking** — per-session ACU consumption and total cost across all sessions
- **Duration tracking** — Overall (webhook → PR) and Devin (session creation → exit) in milliseconds
- **Live indicator** — auto-refreshes every 30 seconds with a pulse dot

The UI follows [Figma's 7 UI design principles](https://www.figma.com/resource-library/ui-design-principles/) and [16 practical UI tips](https://github.com/johndelatto/step-by-step-ui-design-case-study-to-quickly-fix-an-example-user-interface-using-ui-design-tips): design tokens, WCAG AA contrast, responsive layout, visual hierarchy, and keyboard accessibility.

---

## Issue Generator (Testing Tool)

A companion container that creates test issues on your target repository from a curated pool of 50 real Apache Superset issues. See [`tests/issue-generator/README.md`](tests/issue-generator/README.md) for full documentation.

**Quick start:**

```bash
# Build the generator image
podman build -t issue-generator tests/issue-generator/

# Create 3 random test issues (mount file so removals persist)
podman run --env-file .env \
  -v $(pwd)/tests/issue-generator/issues.md:/app/issues.md \
  issue-generator --batch 3
```

**Key features:**
- **Random selection** — each run picks random issues from the pool (not sequential)
- **Shrinking queue** — created issues are removed from `issues.md` so they won't repeat
- **Type-prefixed titles** — issues are titled `[Bug]`, `[Feature]`, or `[Task]` to work with the title prefix fallback
- **Reuses `.env`** — only needs `GITHUB_TOKEN` and `REPOSITORY_URL` from your existing config
- **Dry run** — use `--dry-run` to preview without creating issues

> **Important:** Mount `issues.md` with `-v` so removals persist between container runs. Without it, each run starts from the original 50-issue pool.

---

## Alternative: Docker Compose

If you prefer Docker Compose over standalone Podman:

```bash
docker-compose up --build
```

This builds the image and starts the container with persistent storage and auto-restart.

---

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Lint** — `ruff check` and `ruff format --check` on all Python files
- **Test** — `pytest` runs all tests
- **Docker build** — Verifies the Docker image builds successfully

CI runs on every push to `main` and on all pull requests.

---

## Development

### Run locally (without container)

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

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/webhook` | POST | GitHub webhook receiver |
| `/dashboard` | GET | Remediation Operations Dashboard |
| `/health` | GET | Health check |

## Tech Stack

| Component | Technology |
|---|---|
| Webhook listener | Python + Flask |
| Async processing | Python threading |
| Session manager | Python + requests (Devin API v3) |
| Observability store | SQLite |
| Dashboard | Flask + Jinja2 |
| Containerisation | Podman / Docker |
| Tunnel | ngrok |
| CI | GitHub Actions |
