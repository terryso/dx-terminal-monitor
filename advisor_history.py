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

from config import ADVISOR_HISTORY_MAX, ADVISOR_SURGE_DOMAIN, SURGE_TOKEN

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


SURGE_TOKEN_FILE = Path.home() / ".surge" / "token"


def _get_surge_token() -> str | None:
    """Get surge token from config or file.

    Priority: config.SURGE_TOKEN > ~/.surge/token
    """
    if SURGE_TOKEN:
        return SURGE_TOKEN
    if SURGE_TOKEN_FILE.exists():
        return SURGE_TOKEN_FILE.read_text().strip()
    return None


def sync_to_surge():
    """Sync data directory to surge.sh with retry.

    Logs failure but does not raise exception.
    """
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            token = _get_surge_token()
            cmd = ["surge", str(WEB_DIR), ADVISOR_SURGE_DOMAIN]
            if token:
                cmd.extend(["--token", token])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info(f"Synced to surge.sh: https://{ADVISOR_SURGE_DOMAIN}")
                return  # Success
            else:
                logger.warning(f"Surge sync failed (attempt {attempt + 1}/{max_retries}): {result.stderr}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)

        except FileNotFoundError:
            logger.warning("Surge CLI not installed, skip sync")
            return
        except subprocess.TimeoutExpired:
            logger.warning(f"Surge sync timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Surge sync error: {e}")
            return

    logger.error(f"Surge sync failed after {max_retries} attempts")


def get_view_url() -> str:
    """Get the URL to view analysis history."""
    return f"https://{ADVISOR_SURGE_DOMAIN}"
