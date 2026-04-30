# Product Requirements Document
## Event-Driven Issue Remediation System
**Author:** Anand Rai
**Version:** 1.1
**Date:** April 2026
**Status:** Draft

---

## 1. Problem Statement

Engineering teams at scale face a growing and unmanageable backlog of issues — bugs, feature requests, and maintenance tasks. Manual remediation is slow, inconsistent, and expensive — it requires engineers to context-switch, understand unfamiliar code, write fixes or features, test them, and open pull requests. This process takes hours per issue and weeks at backlog scale.

**The business cost is threefold:**
- Issues remain open while they sit unaddressed in the backlog
- Engineer productivity is degraded by context-switching between issue types
- Delivery velocity drops as backlogs grow faster than teams can address them

**Root cause:** Issue remediation is a well-scoped, repeatable engineering task that is currently dependent on human engineers despite being highly automatable.

---

## 2. Objective

Build a production-grade, event-driven automation system that:
- Detects newly created or labelled issues in a GitHub repository (bugs, features, tasks)
- Automatically initiates an AI agent session to analyse and resolve each issue
- Produces auditable, reviewable outputs — pull requests with fixes and tests
- Gives engineering leadership real-time visibility into system health and effectiveness
- Scales across repositories and organisations without linear growth in engineering effort

---

## 3. Target Users

| User | Role | Primary Need |
|---|---|---|
| VP of Engineering | Economic buyer | Reduce issue backlog without consuming engineer time. Measurable velocity improvement. |
| Senior Engineers | Technical reviewers | Trust that AI-generated fixes are correct, well-tested, and follow team conventions before merging |
| Product / Project Managers | Stakeholders | Audit trail showing every issue was identified, assigned, actioned, and resolved with timestamps |
| DevOps / Platform Engineering | Operators | System runs reliably, is observable, integrates with existing toolchain, and fails gracefully |

---

## 4. Scope

### In Scope — Version 1.1
- Webhook listener triggered by GitHub issue creation with configurable labels (default: `bug`, `feature`, `task`)
- Support for all standard GitHub issue types: bugs, features, and tasks
- AI agent session manager — creates, monitors, and tracks remediation sessions via Devin API
- Idempotent session handling — prevents duplicate remediations for the same issue
- Observability layer — logs session lifecycle, PR output, success/failure signals, time-to-remediation
- Operational dashboard — real-time view of system health and remediation throughput
- Docker containerisation for reproducible, portable deployment
- GitHub Actions CI pipeline (lint, test, Docker build)

### Out of Scope — Future Phases
- Automatic vulnerability scanning (Snyk, Dependabot, SAST tool integration)
- Multi-repository support
- Slack / PagerDuty / email notifications
- Cost-per-remediation tracking
- AI-based severity triage before triggering remediation
- Auto-merge of approved PRs
- JIRA / Linear issue tracker integration

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Repository                      │
│  Issue created with label: bug / feature / task           │
└─────────────────────────┬───────────────────────────────┘
                          │ Webhook POST
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Webhook Listener Service                    │
│  • Validates GitHub webhook signature (HMAC-SHA256)      │
│  • Filters for configured issue labels                   │
│  • Returns 200 immediately                               │
│  • Enqueues remediation job asynchronously               │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Remediation Orchestrator                    │
│  • Checks idempotency — skip if session already exists   │
│  • Builds structured prompt from issue context           │
│  • Calls Devin API to create session                     │
│  • Polls session status until terminal state             │
│  • Extracts PR URL from completed session                │
│  • Handles failures gracefully with retry logic          │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
               ▼                      ▼
┌──────────────────────┐   ┌──────────────────────────────┐
│     Devin API        │   │      Observability Store      │
│   (External)         │   │  • SQLite session log         │
│                      │   │  • Lifecycle timestamps        │
│  Analyses issue      │   │  • Status transitions         │
│  Writes fix          │   │  • PR URLs                    │
│  Opens PR in repo    │   │  • Error messages             │
│                      │   │  • Time-to-remediation        │
└──────────────────────┘   └──────────────┬───────────────┘
                                          │
                                          ▼
                           ┌──────────────────────────────┐
                           │     Operations Dashboard      │
                           │  • Active / completed / failed│
                           │  • Session list with PR links │
                           │  • Success rate               │
                           │  • Average time-to-remediation│
                           │  • Auto-refresh               │
                           └──────────────────────────────┘
```

---

## 6. Functional Requirements

### 6.1 Webhook Listener

| ID | Requirement | Priority |
|---|---|---|
| WH-01 | Accept POST requests on `/webhook` endpoint | Must Have |
| WH-02 | Validate GitHub webhook signature using HMAC-SHA256 and shared secret | Must Have |
| WH-03 | Return HTTP 200 immediately before processing — webhook delivery must not time out | Must Have |
| WH-04 | Filter events — only process `issues.opened` or `issues.labeled` events | Must Have |
| WH-05 | Only trigger remediation for issues containing at least one configured label | Must Have |
| WH-06 | Process remediation jobs asynchronously — decouple from HTTP response | Must Have |
| WH-07 | Handle malformed payloads gracefully — log and discard without crashing | Must Have |
| WH-08 | Support configurable label list via environment variable (default: `bug,feature,task`) | Should Have |

---

### 6.2 Remediation Orchestrator

| ID | Requirement | Priority |
|---|---|---|
| RO-01 | Check idempotency before creating a session — if a session already exists for this issue number, skip | Must Have |
| RO-02 | Build structured prompt from issue context: repository URL, issue number, title, body | Must Have |
| RO-03 | Call Devin API to create a new remediation session | Must Have |
| RO-04 | Pass `idempotent_client_id` keyed on issue number to prevent duplicate Devin sessions | Must Have |
| RO-05 | Poll session status at configurable interval (default: 30 seconds) until terminal state | Must Have |
| RO-06 | Extract pull request URL from completed session output | Must Have |
| RO-07 | Handle session failure — log error details, do not retry automatically in v1.0 | Must Have |
| RO-08 | Implement session timeout — mark as failed if session exceeds configurable limit (default: 45 minutes) | Must Have |
| RO-09 | Log all state transitions with timestamps | Must Have |
| RO-10 | Support configurable polling interval via environment variable | Should Have |
| RO-11 | Support configurable session timeout via environment variable | Should Have |

---

### 6.3 Devin Prompt Design

The quality of remediation depends directly on prompt quality. Each session receives a structured prompt tailored to the issue type:

```
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

Scope: Do not make changes beyond what is required to resolve this specific issue.
```

**Issue type to PR prefix mapping:**
| Label | PR Prefix |
|---|---|
| `bug` | `fix:` |
| `feature` | `feat:` |
| `task` | `chore:` |

| ID | Requirement | Priority |
|---|---|---|
| PR-01 | Prompt must include repository URL, issue number, title, and full body | Must Have |
| PR-02 | Prompt must instruct Devin to open a PR referencing the issue | Must Have |
| PR-03 | Prompt must constrain scope — fixes only, no unrelated changes | Must Have |
| PR-04 | Prompt must require test coverage for the fix | Must Have |
| PR-05 | Prompt template must be configurable via environment or config file | Should Have |

---

### 6.4 Observability Store

| ID | Requirement | Priority |
|---|---|---|
| OB-01 | Persist all session records to SQLite database | Must Have |
| OB-02 | Store: session_id, issue_number, issue_title, status, created_at, updated_at, completed_at | Must Have |
| OB-03 | Store PR URL on successful session completion | Must Have |
| OB-04 | Store error message and error type on session failure | Must Have |
| OB-05 | Calculate and store time_to_remediation_seconds on completion | Must Have |
| OB-06 | Support status values: `created`, `running`, `completed`, `failed`, `timed_out` | Must Have |
| OB-07 | Database must persist across container restarts via volume mount | Must Have |

**Schema:**
```sql
CREATE TABLE sessions (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id                  TEXT UNIQUE NOT NULL,
    issue_number                INTEGER NOT NULL,
    issue_title                 TEXT NOT NULL,
    repository_url              TEXT NOT NULL,
    status                      TEXT NOT NULL,
    pr_url                      TEXT,
    error_message               TEXT,
    error_type                  TEXT,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at                TIMESTAMP,
    time_to_remediation_seconds INTEGER
);

CREATE INDEX idx_issue_number ON sessions(issue_number);
CREATE INDEX idx_status ON sessions(status);
```

---

### 6.5 Operations Dashboard

| ID | Requirement | Priority |
|---|---|---|
| DB-01 | Display count of sessions by status: active, completed, failed | Must Have |
| DB-02 | Display overall success rate as percentage | Must Have |
| DB-03 | Display average time-to-remediation across all completed sessions | Must Have |
| DB-04 | List all sessions with: issue number, title, status, PR link, created time | Must Have |
| DB-05 | PR links must be clickable — open in new tab | Must Have |
| DB-06 | Dashboard accessible at `/dashboard` | Must Have |
| DB-07 | Auto-refresh every 30 seconds | Should Have |
| DB-08 | Filter sessions by status | Should Have |
| DB-09 | Show session timeline — time spent in each status | Could Have |

---

## 7. Non-Functional Requirements

### 7.1 Reliability

| ID | Requirement |
|---|---|
| NF-01 | Webhook listener must return 200 within 2 seconds regardless of downstream processing time |
| NF-02 | System must handle Devin API unavailability gracefully — queue jobs for retry |
| NF-03 | System must handle GitHub API rate limiting — implement exponential backoff |
| NF-04 | No data loss on container restart — all state persisted to durable storage |

### 7.2 Idempotency

| ID | Requirement |
|---|---|
| NF-05 | Processing the same issue event twice must not create duplicate Devin sessions |
| NF-06 | Restarting the container must not re-trigger already-completed remediations |

### 7.3 Security

| ID | Requirement |
|---|---|
| NF-07 | GitHub webhook signature must be validated on every request |
| NF-08 | API keys must be injected via environment variables — never hardcoded |
| NF-09 | No API keys or secrets must appear in logs |

### 7.4 Observability

| ID | Requirement |
|---|---|
| NF-10 | Every state transition must be logged with timestamp and session ID |
| NF-11 | Structured logs must include: timestamp, level, session_id, issue_number, event_type, message |
| NF-12 | Errors must include full stack trace in logs |

### 7.5 Portability

| ID | Requirement |
|---|---|
| NF-13 | Full system must start via `docker-compose up` with no manual steps beyond providing API keys |
| NF-14 | All configuration must be injectable via environment variables |
| NF-15 | README must enable a new engineer to run the system in under 10 minutes |

---

## 8. Configuration Reference

All configuration injected via environment variables:

| Variable | Description | Default | Required |
|---|---|---|---|
| `GITHUB_WEBHOOK_SECRET` | Shared secret for webhook signature validation | — | Yes |
| `DEVIN_API_KEY` | Devin API authentication key | — | Yes |
| `GITHUB_TOKEN` | GitHub personal access token for PR operations | — | Yes |
| `REPOSITORY_URL` | Target GitHub repository URL | — | Yes |
| `ISSUE_LABELS` | Comma-separated list of issue labels that trigger remediation | `bug,feature,task` | No |
| `POLLING_INTERVAL_SECONDS` | How often to poll Devin session status | `30` | No |
| `SESSION_TIMEOUT_MINUTES` | Max session duration before marking timed out | `45` | No |
| `DATABASE_PATH` | Path to SQLite database file | `/data/sessions.db` | No |
| `DASHBOARD_PORT` | Port for operations dashboard | `5000` | No |

---

## 9. Tech Stack

| Component | Technology | Rationale |
|---|---|---|
| Webhook listener | Python + Flask | Lightweight, fast to build, production-proven for webhook handling |
| Async processing | Python threading / queue | Decouples webhook response from processing without complex infrastructure |
| Session manager | Python + requests | Clean HTTP client for Devin API calls |
| Observability store | SQLite | Zero-dependency, sufficient for single-repository scale, durable |
| Dashboard | Flask + Jinja2 | Simple server-rendered HTML, no frontend build step required |
| Containerisation | Docker + docker-compose | Reproducible, portable, single-command deployment |

---

## 10. Success Criteria

The system is considered production-ready when:

| Criteria | Measurement |
|---|---|
| Event triggering | A GitHub issue labelled `bug`, `feature`, or `task` triggers a Devin session within 60 seconds — without manual intervention |
| Remediation quality | Devin successfully opens a pull request with a fix and tests in ≥ 70% of triggered sessions |
| Idempotency | Creating the same issue twice does not create duplicate sessions |
| Observability | Dashboard accurately reflects all session states and PR outcomes in real time |
| Portability | System starts cleanly via `docker-compose up` on a fresh machine with only API keys provided |
| Reliability | System recovers from container restart without data loss or duplicate processing |

---

## 11. Future Roadmap

| Phase | Feature | Value |
|---|---|---|
| v1.1 | Automatic vulnerability scanning integration (Snyk, Dependabot) | Removes manual issue creation — fully autonomous pipeline |
| v1.2 | AI-based severity triage — classify issues before triggering Devin | Prioritise critical vulnerabilities, skip low-risk issues |
| v1.3 | Slack / PagerDuty notifications on completion and failure | Operational awareness without checking dashboard |
| v1.4 | Multi-repository support | Scale across an organisation's full GitHub footprint |
| v1.5 | Cost-per-remediation tracking | Build ROI case for engineering leadership |
| v2.0 | Auto-merge approved PRs with passing CI | Fully autonomous remediation pipeline — zero human touchpoints for low-risk fixes |

---

*PRD Version 1.1 — Anand Rai — April 2026*

---

## Changelog

### v1.1 (April 2026)
- **Expanded issue type support**: System now handles `bug`, `feature`, and `task` labels (previously only `vulnerability`)
- **Multi-label configuration**: `VULNERABILITY_LABEL` replaced by `ISSUE_LABELS` (comma-separated)
- **Type-aware prompts**: Prompt builder maps issue types to conventional commit prefixes (`fix:`, `feat:`, `chore:`)
- **GitHub Actions CI**: Added lint (ruff), test (pytest), and Docker build jobs
- **Updated PRD to v1.1** reflecting expanded scope
