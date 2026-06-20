"""
save_manager.py
Manages up to NUM_SLOTS JSON save files on disk.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from utils import data_path

NUM_SLOTS = 3


@dataclass
class SaveInfo:
    """Summary of a save slot shown in the Load/Save UI."""
    slot: int
    story_title: str
    chapter: str
    timestamp: str
    story_path: str
    raw: dict  # full serialised data for restoration


class SaveManager:
    """Reads and writes JSON save files in the user-writable data directory."""

    def __init__(self) -> None:
        self._saves_dir = Path(data_path("saves"))
        self._saves_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    def _slot_path(self, slot: int) -> Path:
        return self._saves_dir / f"save_{slot}.json"

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, slot: int, game_state, story_path: str) -> None:
        """Serialise *game_state* to slot *slot*."""
        data = game_state.to_dict()
        data["story_title"] = game_state.story.meta.title
        data["story_path"] = story_path
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["slot"] = slot

        with open(self._slot_path(slot), "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load_raw(self, slot: int) -> Optional[dict]:
        """Return the raw dict from slot *slot*, or None if the slot is empty."""
        path = self._slot_path(slot)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None

    def get_slot_info(self, slot: int) -> Optional[SaveInfo]:
        """Return a SaveInfo summary for *slot*, or None if the slot is empty."""
        raw = self.load_raw(slot)
        if raw is None:
            return None
        return SaveInfo(
            slot=slot,
            story_title=raw.get("story_title", "Unknown"),
            chapter=raw.get("chapter", ""),
            timestamp=raw.get("timestamp", ""),
            story_path=raw.get("story_path", ""),
            raw=raw,
        )

    def get_all_slots(self) -> list[Optional[SaveInfo]]:
        """Return SaveInfo (or None) for all NUM_SLOTS slots."""
        return [self.get_slot_info(i) for i in range(1, NUM_SLOTS + 1)]

    def has_any_save(self) -> bool:
        return any(self._slot_path(i).exists() for i in range(1, NUM_SLOTS + 1))

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, slot: int) -> None:
        path = self._slot_path(slot)
        if path.exists():
            path.unlink()
