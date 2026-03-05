"""
Analysis History Storage Module for Story 8-6

Stores AI analysis history with full request/response for debugging.
"""

import json
import logging
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

from config import ADVISOR_HISTORY_MAX, ADVISOR_SURGE_DOMAIN

logger = logging.getLogger(__name__)

# File paths
HISTORY_FILE = Path("data/advisor_history.json")
WEB_DIR = Path("data")  # index.html and advisor_history.json both live here


def save_analysis(request: str, response: str, suggestions: list) -> str:
    """Save analysis record and return record ID.

    Args:
        request: Full prompt sent to LLM (system + user message)
        response: Raw LLM response
        suggestions: Parsed suggestions list

    Returns:
        8-character record ID
    """
    history = load_history()

    record_id = uuid.uuid4().hex[:8]
    record = {
        "id": record_id,
        "timestamp": datetime.now().isoformat(),
        "request": request,
        "response": response,
        "suggestions": suggestions,
    }

    history.insert(0, record)

    # Limit records
    if len(history) > ADVISOR_HISTORY_MAX:
        history = history[:ADVISOR_HISTORY_MAX]

    _save_history(history)
    logger.info(f"Saved analysis record: {record_id}")
    return record_id


def load_history() -> list:
    """Load analysis history from file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load history: {e}")
        return []


def _save_history(history: list):
    """Save history to file."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def sync_to_surge():
    """Sync data directory to surge.sh.

    Logs failure but does not raise exception.
    """
    try:
        result = subprocess.run(
            ["surge", str(WEB_DIR), ADVISOR_SURGE_DOMAIN],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            logger.info(f"Synced to surge.sh: https://{ADVISOR_SURGE_DOMAIN}")
        else:
            logger.warning(f"Surge sync failed: {result.stderr}")

    except FileNotFoundError:
        logger.warning("Surge CLI not installed, skip sync")
    except subprocess.TimeoutExpired:
        logger.warning("Surge sync timeout")
    except Exception as e:
        logger.error(f"Surge sync error: {e}")


def get_view_url() -> str:
    """Get the URL to view analysis history."""
    return f"https://{ADVISOR_SURGE_DOMAIN}"
