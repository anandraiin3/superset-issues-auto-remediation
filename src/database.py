"""SQLite observability store.

OB-01 – OB-07: Persists session records with full lifecycle tracking.
"""

import re
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional

from src.config import Config
from src.logger import get_logger

logger = get_logger(__name__)

_local = threading.local()


def _get_connection() -> sqlite3.Connection:
    """Return a thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(Config.DATABASE_PATH)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
    return _local.conn


def reset_connection() -> None:
    """Close and discard the thread-local connection (useful for tests)."""
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None


def init_db() -> None:
    """Create tables and indices if they do not exist."""
    conn = _get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id                  TEXT UNIQUE NOT NULL,
            issue_number                INTEGER NOT NULL,
            issue_title                 TEXT NOT NULL,
            repository_url              TEXT NOT NULL,
            status                      TEXT NOT NULL,
            status_detail               TEXT,
            devin_url                   TEXT,
            pr_url                      TEXT,
            error_message               TEXT,
            error_type                  TEXT,
            last_posted_message_id      TEXT,
            acus_consumed               REAL DEFAULT 0,
            created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at                TIMESTAMP,
            devin_started_at            TIMESTAMP,
            pr_raised_at                TIMESTAMP,
            time_to_remediation_seconds INTEGER
        );

        -- Migrate existing tables: add columns if missing
        -- (SQLite ignores ALTER TABLE ADD COLUMN if column exists when
        --  wrapped in a try/except at the Python level; we handle it below.)

        CREATE UNIQUE INDEX IF NOT EXISTS idx_issue_number ON sessions(issue_number);
        CREATE INDEX IF NOT EXISTS idx_status ON sessions(status);
        """
    )
    conn.commit()

    # Migrate: add new columns to existing tables (idempotent).
    for col_def in (
        "status_detail TEXT",
        "devin_url TEXT",
        "last_posted_message_id TEXT",
        "acus_consumed REAL DEFAULT 0",
        "devin_started_at TIMESTAMP",
        "pr_raised_at TIMESTAMP",
    ):
        try:
            conn.execute(f"ALTER TABLE sessions ADD COLUMN {col_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists

    logger.info("Database initialised", extra={"event_type": "db_init"})


def title_already_remediated(issue_title: str) -> bool:
    """Check whether a session with the same normalised title already exists.

    Strips a leading ``[Type] `` prefix (if any) so that e.g.
    ``[Bug] Fix overlap`` matches an earlier ``[Bug] Fix overlap`` even if
    it was filed under a different issue number.  Only non-terminal failed
    sessions are excluded — completed, running, and created sessions all
    count as "already handled".
    """
    conn = _get_connection()
    normalised = re.sub(r"^\[\w+\]\s*", "", issue_title).strip().lower()
    rows = conn.execute(
        "SELECT issue_title FROM sessions WHERE status != 'failed'"
    ).fetchall()
    for row in rows:
        existing = re.sub(r"^\[\w+\]\s*", "", row["issue_title"]).strip().lower()
        if existing == normalised:
            return True
    return False


def session_exists_for_issue(issue_number: int) -> bool:
    """NF-05 / RO-01: Check whether a session already exists for this issue."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT 1 FROM sessions WHERE issue_number = ? LIMIT 1",
        (issue_number,),
    ).fetchone()
    return row is not None


def reserve_issue(issue_number: int, issue_title: str, repository_url: str) -> bool:
    """Atomically reserve an issue number for remediation.

    Inserts a placeholder row with a temporary session_id.  Returns True
    if the reservation succeeded (i.e. no prior session exists for this
    issue).  Returns False if a row already exists (UNIQUE constraint on
    issue_number).

    This eliminates the TOCTOU race between session_exists_for_issue()
    and create_session() — the INSERT itself acts as the lock.
    """
    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO sessions (session_id, issue_number, issue_title, repository_url, status)
            VALUES (?, ?, ?, ?, 'created')
            """,
            (f"pending-{issue_number}", issue_number, issue_title, repository_url),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # duplicate — another thread already reserved this issue


def create_session(
    session_id: str,
    issue_number: int,
    issue_title: str,
    repository_url: str,
    devin_url: str = "",
) -> None:
    """Update the placeholder row with the real Devin session details."""
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        UPDATE sessions
        SET session_id = ?, devin_url = ?, devin_started_at = ?
        WHERE issue_number = ? AND session_id = ?
        """,
        (session_id, devin_url, now, issue_number, f"pending-{issue_number}"),
    )
    conn.commit()
    logger.info(
        "Session created in DB",
        extra={
            "session_id": session_id,
            "issue_number": issue_number,
            "event_type": "session_created",
        },
    )


def update_session_status(
    session_id: str,
    status: str,
    status_detail: Optional[str] = None,
    pr_url: Optional[str] = None,
    error_message: Optional[str] = None,
    error_type: Optional[str] = None,
    acus_consumed: Optional[float] = None,
) -> None:
    """Transition session to a new status with appropriate metadata."""
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()

    # Record pr_raised_at the first time a PR URL appears
    pr_raised_update = ""
    pr_raised_param: list = []
    if pr_url:
        row = conn.execute(
            "SELECT pr_raised_at FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row and not row["pr_raised_at"]:
            pr_raised_update = ", pr_raised_at = ?"
            pr_raised_param = [now]

    if status in ("completed", "failed", "timed_out"):
        # Calculate time-to-remediation
        row = conn.execute(
            "SELECT created_at FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        ttr = None
        if row:
            created = datetime.fromisoformat(row["created_at"])
            created_aware = (
                created.replace(tzinfo=timezone.utc)
                if created.tzinfo is None
                else created
            )
            ttr = int((datetime.now(timezone.utc) - created_aware).total_seconds())

        conn.execute(
            f"""
            UPDATE sessions
            SET status = ?,
                status_detail = COALESCE(?, status_detail),
                pr_url = COALESCE(?, pr_url),
                error_message = COALESCE(?, error_message),
                error_type = COALESCE(?, error_type),
                acus_consumed = COALESCE(?, acus_consumed),
                updated_at = ?,
                completed_at = ?,
                time_to_remediation_seconds = ?
                {pr_raised_update}
            WHERE session_id = ?
            """,
            (
                status,
                status_detail,
                pr_url,
                error_message,
                error_type,
                acus_consumed,
                now,
                now,
                ttr,
                *pr_raised_param,
                session_id,
            ),
        )
    else:
        conn.execute(
            f"""
            UPDATE sessions
            SET status = ?,
                status_detail = COALESCE(?, status_detail),
                pr_url = COALESCE(?, pr_url),
                acus_consumed = COALESCE(?, acus_consumed),
                updated_at = ?
                {pr_raised_update}
            WHERE session_id = ?
            """,
            (
                status,
                status_detail,
                pr_url,
                acus_consumed,
                now,
                *pr_raised_param,
                session_id,
            ),
        )
    conn.commit()
    logger.info(
        f"Session status -> {status}",
        extra={
            "session_id": session_id,
            "event_type": "status_transition",
        },
    )


def get_session(session_id: str) -> Optional[dict]:
    """Return a single session record by session_id."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    return dict(row) if row else None


def update_last_posted_message(session_id: str, message_id: str) -> None:
    """Track the last Devin message that was posted to the GitHub issue."""
    conn = _get_connection()
    conn.execute(
        "UPDATE sessions SET last_posted_message_id = ? WHERE session_id = ?",
        (message_id, session_id),
    )
    conn.commit()


def _ts_to_aware(raw: str) -> datetime:
    """Parse an ISO timestamp and ensure it is UTC-aware."""
    dt = datetime.fromisoformat(raw)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _enrich_durations(row: dict) -> dict:
    """Add computed overall_time_ms and devin_time_ms to a session dict."""
    # Overall time: webhook trigger (created_at) → PR raised (pr_raised_at)
    overall_ms: Optional[int] = None
    if row.get("created_at") and row.get("pr_raised_at"):
        delta = _ts_to_aware(row["pr_raised_at"]) - _ts_to_aware(row["created_at"])
        overall_ms = int(delta.total_seconds() * 1000)

    # Devin time: session creation (devin_started_at) → session exit (completed_at)
    devin_ms: Optional[int] = None
    if row.get("devin_started_at") and row.get("completed_at"):
        delta = _ts_to_aware(row["completed_at"]) - _ts_to_aware(
            row["devin_started_at"]
        )
        devin_ms = int(delta.total_seconds() * 1000)

    row["overall_time_ms"] = overall_ms
    row["devin_time_ms"] = devin_ms
    return row


def get_all_sessions() -> list[dict]:
    """Return all session records ordered by most recent first."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC").fetchall()
    return [_enrich_durations(dict(r)) for r in rows]


def get_sessions_by_status(status: str) -> list[dict]:
    """Return sessions filtered by status."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions WHERE status = ? ORDER BY created_at DESC",
        (status,),
    ).fetchall()
    return [_enrich_durations(dict(r)) for r in rows]


def get_dashboard_stats() -> dict:
    """Aggregate stats for the operations dashboard."""
    conn = _get_connection()

    total = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
    by_status = {}
    for row in conn.execute(
        "SELECT status, COUNT(*) AS c FROM sessions GROUP BY status"
    ):
        by_status[row["status"]] = row["c"]

    completed = by_status.get("completed", 0)
    failed = by_status.get("failed", 0) + by_status.get("timed_out", 0)
    active = by_status.get("created", 0) + by_status.get("running", 0)

    success_rate = (completed / total * 100) if total > 0 else 0.0

    # Compute average overall time (webhook → PR) in ms for completed sessions
    rows_with_pr = conn.execute(
        "SELECT created_at, pr_raised_at FROM sessions WHERE pr_raised_at IS NOT NULL"
    ).fetchall()
    overall_ms_values = []
    for r in rows_with_pr:
        if r["created_at"] and r["pr_raised_at"]:
            delta = _ts_to_aware(r["pr_raised_at"]) - _ts_to_aware(r["created_at"])
            overall_ms_values.append(int(delta.total_seconds() * 1000))
    avg_overall_ms = (
        int(sum(overall_ms_values) / len(overall_ms_values)) if overall_ms_values else 0
    )

    total_cost_row = conn.execute(
        "SELECT COALESCE(SUM(acus_consumed), 0) AS total_cost FROM sessions"
    ).fetchone()
    total_cost = total_cost_row["total_cost"]

    return {
        "total": total,
        "active": active,
        "completed": completed,
        "failed": failed,
        "success_rate": round(success_rate, 1),
        "avg_overall_ms": avg_overall_ms,
        "total_cost_acus": round(total_cost, 2),
        "by_status": by_status,
    }
