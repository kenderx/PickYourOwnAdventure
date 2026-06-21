"""
game_screen.py
Core gameplay screen.

Layout (top → bottom):
    StatusBar      — chapter title, menu + sheet buttons
    PassagePanel   — scrollable story text (typewriter animated)
    ChoicePanel    — numbered choice buttons

When a choice is made: effects run, node advances, panels refresh.
Music and SFX are handed to app.audio.
"""
from __future__ import annotations

import customtkinter as ctk

from ui.components.passage_panel import PassagePanel
from ui.components.choice_panel import ChoicePanel
from ui.components.status_bar import StatusBar


class GameScreen(ctk.CTkFrame):
    """The primary gameplay view."""

    # Rough ratio of screen height devoted to story text vs. choices
    PASSAGE_WEIGHT = 3
    CHOICE_WEIGHT  = 2

    def __init__(self, parent, app) -> None:
        c = app.colors
        super().__init__(parent, fg_color=c["bg_primary"], corner_radius=0)
        self.app = app
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        c = self.app.colors

        # Configure vertical layout
        self.grid_rowconfigure(0, weight=0)   # status bar  — fixed
        self.grid_rowconfigure(1, weight=self.PASSAGE_WEIGHT)
        self.grid_rowconfigure(2, weight=self.CHOICE_WEIGHT)
        self.grid_columnconfigure(0, weight=1)

        # ---- Status bar ----
        self._status_bar = StatusBar(
            self, self.app,
            on_menu=self._open_pause,
            on_character_sheet=self._open_character_sheet,
        )
        self._status_bar.grid(row=0, column=0, sticky="ew")

        # ---- Passage panel ----
        self._passage = PassagePanel(self, self.app)
        self._passage.grid(
            row=1, column=0,
            sticky="nsew",
            padx=16, pady=(10, 6),
        )

        # ---- Divider ----
        divider = ctk.CTkFrame(self, fg_color=c["separator"], height=1, corner_radius=0)
        divider.grid(row=1, column=0, sticky="sew", padx=16)

        # ---- Choice panel ----
        self._choices = ChoicePanel(
            self, self.app,
            on_choice_selected=self._on_choice,
        )
        self._choices.grid(
            row=2, column=0,
            sticky="nsew",
            padx=0, pady=0,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_show(self, **kwargs) -> None:
        """Called each time the game screen becomes active."""
        gs = self.app.game_state
        if gs is None:
            return
        self._render_node()

    # ------------------------------------------------------------------
    # Node rendering
    # ------------------------------------------------------------------

    def _render_node(self) -> None:
        """Refresh UI to match the current node in game_state."""
        gs   = self.app.game_state
        node = gs.current_node()

        # Status bar
        self._status_bar.update_node(
            gs.story.meta.title,
            node.title or "",
        )

        # Audio — music
        if node.music:
            self.app.audio.play_music(node.music)
        # (keep existing music if node.music is None)

        # Audio — node entry SFX
        if node.sfx:
            self.app.audio.play_sfx(node.sfx)

        # Passage text
        visible_choices = gs.visible_choices()
        self._passage.display(
            node.text,
            on_complete=lambda: self._choices.display_choices(
                visible_choices, is_ending=gs.is_game_over()
            ),
        )

        # Show choices immediately if text_speed is very high (skip animation feel)
        if self.app.settings.text_speed >= 100:
            self._passage.skip_animation()

        # Panel image
        self._passage.set_panel_image(node.panel_image)

    # ------------------------------------------------------------------
    # Choice handling
    # ------------------------------------------------------------------

    def _on_choice(self, choice) -> None:
        """Called when the player taps a choice button."""
        self._choices.clear()

        gs = self.app.game_state
        gs.apply_choice(choice)

        self._render_node()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _open_pause(self) -> None:
        self.app.audio.pause_music()
        self.app.show_screen("pause", mode="in_game")

    def _open_character_sheet(self) -> None:
        self.app.show_screen("character_sheet", return_to="game")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_primary"])
        self._status_bar.apply_theme()
        self._passage.apply_theme()
        self._choices.apply_theme()
