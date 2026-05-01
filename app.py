"""Flask application entrypoint.

Wires together the webhook listener, dashboard, and database
initialisation.  Validates configuration on startup.
"""

import os
import sys

from flask import Flask

from src.config import Config
from src.database import init_db
from src.dashboard import dashboard_bp
from src.logger import get_logger
from src.webhook import webhook_bp
from src.webhook_registration import register_webhook

logger = get_logger(__name__)


def create_app() -> Flask:
    """Application factory."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    )

    # Validate required configuration
    missing = Config.validate()
    if missing:
        logger.error(
            f"Missing required configuration: {', '.join(missing)}",
            extra={"event_type": "config_error"},
        )
        sys.exit(1)

    # Ensure database directory exists
    db_dir = os.path.dirname(Config.DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # Initialise database
    init_db()

    # Register blueprints
    app.register_blueprint(webhook_bp)
    app.register_blueprint(dashboard_bp)

    # Auto-register webhook on the target repository (idempotent)
    register_webhook()

    # Health-check endpoint
    @app.route("/health")
    def health():  # type: ignore[no-untyped-def]
        return {"status": "healthy"}, 200

    logger.info(
        "Application started",
        extra={"event_type": "app_started"},
    )

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=Config.DASHBOARD_PORT)
