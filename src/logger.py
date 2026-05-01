"""Structured logging configuration.

NF-10 / NF-11 / NF-12: Every state transition logged with timestamp,
level, session_id, issue_number, event_type, message.  Errors include
full stack traces.
"""

import logging
import json
import datetime


class StructuredFormatter(logging.Formatter):
    """Emit JSON-structured log lines."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": record.levelname,
            "session_id": getattr(record, "session_id", None),
            "issue_number": getattr(record, "issue_number", None),
            "event_type": getattr(record, "event_type", None),
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


def get_logger(name: str = "remediation") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
