"""Local JSON Lines storage for confirmed patient records."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

# Path to the local JSONL file
DATA_FILE = os.path.join("data", "records.jsonl")


def save_confirmed(form_dict: dict[str, Any], worker_name: str) -> None:
    """Append one confirmed record with UTC timestamp to data/records.jsonl.

    Never stores raw audio — only the confirmed structured JSON text.
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "worker_name": worker_name or "ASHA Worker",
        **form_dict,
    }
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_all() -> list[dict[str, Any]]:
    """Return all saved patient records as a list of dicts."""
    if not os.path.exists(DATA_FILE):
        return []
    records = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def delete_all() -> None:
    """Clear all records from data/records.jsonl."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.truncate(0)
