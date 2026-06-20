"""
settings_manager.py
Persists user preferences (theme, font size, volumes, etc.) as JSON.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from utils import data_path

SETTINGS_FILE = "settings.json"


@dataclass
class Settings:
    """All user-configurable settings with their defaults."""
    theme: str = "dark"           # dark | light | sepia
    font_size: int = 14           # passage text point size
    text_speed: int = 35          # typewriter chars/second (1–100)
    music_volume: float = 0.70
    sfx_volume: float = 1.00
    window_width: int = 1000
    window_height: int = 720


class SettingsManager:
    """Loads and saves the Settings dataclass from/to a JSON file."""

    def __init__(self) -> None:
        self._path = Path(data_path(SETTINGS_FILE))
        self.settings = self._load()

    # ------------------------------------------------------------------

    def _load(self) -> Settings:
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                # Only keep known fields (ignore stale keys from old versions)
                known = Settings.__dataclass_fields__.keys()
                filtered = {k: v for k, v in data.items() if k in known}
                return Settings(**filtered)
            except Exception:
                pass
        return Settings()

    def save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(asdict(self.settings), fh, indent=2)

    def get(self) -> Settings:
        return self.settings
