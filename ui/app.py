"""
app.py
Root customtkinter window.  Manages the screen stack, shared services
(audio, saves, settings) and theme switching.
"""
from __future__ import annotations

import logging

import customtkinter as ctk

from engine.audio_manager import AudioManager
from engine.save_manager import SaveManager
from engine.settings_manager import SettingsManager
from ui.theme import THEMES, FONTS

logger = logging.getLogger(__name__)


class App(ctk.CTk):
    """
    The single root window.

    All screens are CTkFrame children stacked via grid(); tkraise()
    brings the active screen to the front without destroying others.
    """

    def __init__(self) -> None:
        super().__init__()

        # ---- Services ----
        self.settings_mgr = SettingsManager()
        self.settings = self.settings_mgr.get()
        self.audio = AudioManager()
        self.save_mgr = SaveManager()

        # Push settings into audio
        self.audio.music_volume = self.settings.music_volume
        self.audio.sfx_volume = self.settings.sfx_volume

        # ---- Theme ----
        self._theme_name: str = self.settings.theme
        self.colors: dict = THEMES[self._theme_name]
        ctk.set_appearance_mode("dark")   # always dark at the CTk level
        ctk.set_default_color_theme("blue")

        # ---- Window ----
        self.title("Pick Your Own Adventure")
        w, h = self.settings.window_width, self.settings.window_height
        # Centre on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(800, 600)
        self.configure(fg_color=self.colors["bg_primary"])

        # ---- Container (holds all screens in a stack) ----
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        # ---- Runtime game data ----
        self.game_state = None      # engine.game_state.GameState | None
        self.story_path: str = ""   # path to the currently loaded story.yaml

        # ---- Build all screens ----
        self._screens: dict = {}
        self._build_screens()

        # ---- Start ----
        self.show_screen("main_menu")

        # ---- Window events ----
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------

    def _build_screens(self) -> None:
        """Lazily import and instantiate every screen."""
        from ui.screens.main_menu import MainMenuScreen
        from ui.screens.story_select import StorySelectScreen
        from ui.screens.game_screen import GameScreen
        from ui.screens.pause_menu import PauseMenuScreen
        from ui.screens.settings_screen import SettingsScreen
        from ui.screens.character_sheet import CharacterSheetScreen

        mapping = {
            "main_menu":       MainMenuScreen,
            "story_select":    StorySelectScreen,
            "game":            GameScreen,
            "pause":           PauseMenuScreen,
            "settings":        SettingsScreen,
            "character_sheet": CharacterSheetScreen,
        }

        for name, cls in mapping.items():
            screen = cls(self._container, self)
            screen.grid(row=0, column=0, sticky="nsew")
            self._screens[name] = screen

    def show_screen(self, name: str, **kwargs) -> None:
        """Raise *name* to the top of the stack and call its on_show hook."""
        screen = self._screens.get(name)
        if screen is None:
            logger.error("Unknown screen: %s", name)
            return
        screen.tkraise()
        if hasattr(screen, "on_show"):
            screen.on_show(**kwargs)

    def get_screen(self, name: str):
        return self._screens.get(name)

    # ------------------------------------------------------------------
    # Theme switching
    # ------------------------------------------------------------------

    def apply_theme(self, theme_name: str) -> None:
        """Switch the active colour theme and repaint all screens."""
        if theme_name not in THEMES:
            return
        self._theme_name = theme_name
        self.colors = THEMES[theme_name]
        self.settings.theme = theme_name
        self.configure(fg_color=self.colors["bg_primary"])

        for screen in self._screens.values():
            if hasattr(screen, "apply_theme"):
                screen.apply_theme()

    @property
    def theme_name(self) -> str:
        return self._theme_name

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        # Persist window dimensions
        self.settings.window_width = self.winfo_width()
        self.settings.window_height = self.winfo_height()
        self.settings_mgr.save()
        self.audio.cleanup()
        self.destroy()
