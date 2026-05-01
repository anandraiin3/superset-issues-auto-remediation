"""SQLite observability store.

OB-01 – OB-07: Persists session records with full lifecycle tracking.
"""

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
            created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at                TIMESTAMP,
            time_to_remediation_seconds INTEGER
        );

        -- Migrate existing tables: add columns if missing
        -- (SQLite ignores ALTER TABLE ADD COLUMN if column exists when
        --  wrapped in a try/except at the Python level; we handle it below.)

        CREATE INDEX IF NOT EXISTS idx_issue_number ON sessions(issue_number);
        CREATE INDEX IF NOT EXISTS idx_status ON sessions(status);
        """
    )
    conn.commit()

    # Migrate: add new columns to existing tables (idempotent).
    for col_def in (
        "status_detail TEXT",
        "devin_url TEXT",
        "last_posted_message_id TEXT",
    ):
        try:
            conn.execute(f"ALTER TABLE sessions ADD COLUMN {col_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists

    logger.info("Database initialised", extra={"event_type": "db_init"})


def session_exists_for_issue(issue_number: int) -> bool:
    """NF-05 / RO-01: Check whether a session already exists for this issue."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT 1 FROM sessions WHERE issue_number = ? LIMIT 1",
        (issue_number,),
    ).fetchone()
    return row is not None


def create_session(
    session_id: str,
    issue_number: int,
    issue_title: str,
    repository_url: str,
    devin_url: str = "",
) -> None:
    """Insert a new session record with status 'created'."""
    conn = _get_connection()
    conn.execute(
        """
        INSERT INTO sessions (session_id, issue_number, issue_title, repository_url, status, devin_url)
        VALUES (?, ?, ?, ?, 'created', ?)
        """,
        (session_id, issue_number, issue_title, repository_url, devin_url),
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
) -> None:
    """Transition session to a new status with appropriate metadata."""
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()

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
            """
            UPDATE sessions
            SET status = ?,
                status_detail = COALESCE(?, status_detail),
                pr_url = COALESCE(?, pr_url),
                error_message = COALESCE(?, error_message),
                error_type = COALESCE(?, error_type),
                updated_at = ?,
                completed_at = ?,
                time_to_remediation_seconds = ?
            WHERE session_id = ?
            """,
            (
                status,
                status_detail,
                pr_url,
                error_message,
                error_type,
                now,
                now,
                ttr,
                session_id,
            ),
        )
    else:
        conn.execute(
            """
            UPDATE sessions
            SET status = ?,
                status_detail = COALESCE(?, status_detail),
                pr_url = COALESCE(?, pr_url),
                updated_at = ?
            WHERE session_id = ?
            """,
            (status, status_detail, pr_url, now, session_id),
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


def get_all_sessions() -> list[dict]:
    """Return all session records ordered by most recent first."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def get_sessions_by_status(status: str) -> list[dict]:
    """Return sessions filtered by status."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions WHERE status = ? ORDER BY created_at DESC",
        (status,),
    ).fetchall()
    return [dict(r) for r in rows]


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

    avg_ttr_row = conn.execute(
        "SELECT AVG(time_to_remediation_seconds) AS avg_ttr FROM sessions WHERE status = 'completed'"
    ).fetchone()
    avg_ttr = avg_ttr_row["avg_ttr"] if avg_ttr_row["avg_ttr"] else 0

    return {
        "total": total,
        "active": active,
        "completed": completed,
        "failed": failed,
        "success_rate": round(success_rate, 1),
        "avg_ttr_seconds": int(avg_ttr),
        "by_status": by_status,
    }
