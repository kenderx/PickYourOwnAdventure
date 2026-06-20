"""
main.py
Entry point for Pick Your Own Adventure.
Initialises logging, sets the DPI awareness (Windows), and launches the App.
"""
from __future__ import annotations

import logging
import sys
import os

# ---- DPI awareness on Windows (must be before any tkinter import) ----
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# ---- Ensure the project root is on sys.path when running as a .exe ----
if hasattr(sys, "_MEIPASS"):
    sys.path.insert(0, sys._MEIPASS)  # type: ignore

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

# ---- Launch ----
from ui.app import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
