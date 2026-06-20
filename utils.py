"""
utils.py
Utility helpers — especially path resolution for PyInstaller bundles.
"""
from __future__ import annotations

import os
import sys


def get_bundle_dir() -> str:
    """
    Returns the base directory for read-only bundled resources.

    When running from a PyInstaller .exe, this is sys._MEIPASS (the temp
    directory where the bundle is unpacked). In development it is the
    project root directory.
    """
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir() -> str:
    """
    Returns the base directory for writable user data (saves, settings).

    When running from a PyInstaller .exe, this is the directory containing
    the .exe so files survive across updates. In development it is the
    project root.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative: str) -> str:
    """
    Resolve a path relative to the bundle/project root.
    Use for assets, stories, fonts — anything that ships with the app.
    """
    return os.path.join(get_bundle_dir(), relative)


def data_path(relative: str) -> str:
    """
    Resolve a path relative to the writable data directory.
    Use for saves, settings — anything the user/game writes at runtime.
    """
    return os.path.join(get_data_dir(), relative)


def find_stories_dir() -> str:
    """Return the absolute path to the stories directory."""
    return resource_path("stories")
