"""Application configuration loaded from environment variables."""

import os


def _parse_labels(raw: str) -> list[str]:
    """Parse a comma-separated label string into a list of trimmed names."""
    return [label.strip() for label in raw.split(",") if label.strip()]


class Config:
    """Centralised configuration — all values injectable via environment."""

    GITHUB_WEBHOOK_SECRET: str = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    DEVIN_API_KEY: str = os.environ.get("DEVIN_API_KEY", "")
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
    REPOSITORY_URL: str = os.environ.get("REPOSITORY_URL", "")

    # Comma-separated list of issue labels that trigger remediation.
    # Supports all standard GitHub issue types: bug, feature, task, etc.
    ISSUE_LABELS: list[str] = _parse_labels(
        os.environ.get("ISSUE_LABELS", "bug,feature,task")
    )
    POLLING_INTERVAL_SECONDS: int = int(
        os.environ.get("POLLING_INTERVAL_SECONDS", "30")
    )
    SESSION_TIMEOUT_MINUTES: int = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "45"))
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "/data/sessions.db")
    DASHBOARD_PORT: int = int(os.environ.get("DASHBOARD_PORT", "5000"))

    @classmethod
    def validate(cls) -> list[str]:
        """Return a list of missing required config keys."""
        missing: list[str] = []
        for key in ("GITHUB_WEBHOOK_SECRET", "DEVIN_API_KEY", "REPOSITORY_URL"):
            if not getattr(cls, key):
                missing.append(key)
        return missing
