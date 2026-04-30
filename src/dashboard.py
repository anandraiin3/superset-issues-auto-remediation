"""Operations dashboard.

DB-01 – DB-09: Server-rendered HTML dashboard showing session stats,
session list with PR links, status filters, and auto-refresh.
"""

from flask import Blueprint, render_template, request

from src.database import get_all_sessions, get_dashboard_stats, get_sessions_by_status

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard() -> str:
    """DB-06: Dashboard accessible at /dashboard."""
    status_filter = request.args.get("status", "")
    stats = get_dashboard_stats()

    if status_filter:
        sessions = get_sessions_by_status(status_filter)
    else:
        sessions = get_all_sessions()

    return render_template(
        "dashboard.html",
        stats=stats,
        sessions=sessions,
        status_filter=status_filter,
    )
