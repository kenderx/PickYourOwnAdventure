"""
passage_panel.py
Scrollable story-text panel with a typewriter reveal animation.

The panel exposes:
    display(text)        — start typing *text* character-by-character
    skip_animation()     — jump to full text immediately
    clear()              — reset for a new node
"""
from __future__ import annotations

import tkinter as tk
from typing import Optional

import customtkinter as ctk


class PassagePanel(ctk.CTkFrame):
    """
    Scrollable text widget that reveals story passages with a typewriter effect.

    Click anywhere on the panel (or press Space) to skip to full text.
    """

    def __init__(self, parent, app, **kwargs) -> None:
        c = app.colors
        super().__init__(
            parent,
            fg_color=c["bg_panel"],
            corner_radius=12,
            border_width=1,
            border_color=c["border"],
            **kwargs,
        )
        self.app = app
        self._full_text: str = ""
        self._anim_id: Optional[str] = None  # after() callback id
        self._anim_index: int = 0
        self._on_complete_cb = None           # called when typing finishes

        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        c = self.app.colors
        s = self.app.settings

        # Scrollable text box
        self._textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            state="disabled",
            fg_color=c["bg_panel"],
            text_color=c["text_primary"],
            font=(self.app.settings.theme and "Georgia", s.font_size),
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
            corner_radius=10,
            border_width=0,
            activate_scrollbars=True,
        )
        self._textbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Click to skip
        self._textbox.bind("<Button-1>", lambda e: self.skip_animation())
        self.bind("<Button-1>", lambda e: self.skip_animation())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def display(self, text: str, on_complete=None) -> None:
        """Begin typing *text* with the typewriter effect."""
        self._cancel_animation()
        self._full_text = text
        self._anim_index = 0
        self._on_complete_cb = on_complete

        self._clear_textbox()
        self._tick()

    def skip_animation(self) -> None:
        """Immediately reveal the full text and stop the animation."""
        if self._anim_id is not None:
            self._cancel_animation()
            self._set_text(self._full_text)
            if self._on_complete_cb:
                self._on_complete_cb()

    def clear(self) -> None:
        """Clear all text."""
        self._cancel_animation()
        self._clear_textbox()

    def set_text_direct(self, text: str) -> None:
        """Set text without animation (used when loading a save)."""
        self._cancel_animation()
        self._full_text = text
        self._set_text(text)

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(
            fg_color=c["bg_panel"],
            border_color=c["border"],
        )
        self._textbox.configure(
            fg_color=c["bg_panel"],
            text_color=c["text_primary"],
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
        )

    # ------------------------------------------------------------------
    # Animation internals
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Reveal one more character, then schedule the next tick."""
        if self._anim_index > len(self._full_text):
            # Done
            if self._on_complete_cb:
                self._on_complete_cb()
            return

        self._set_text(self._full_text[: self._anim_index])
        self._anim_index += 1

        speed = max(1, self.app.settings.text_speed)   # chars / second
        delay = int(1000 / speed)                       # ms per char
        self._anim_id = self.after(delay, self._tick)

    def _cancel_animation(self) -> None:
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    def _set_text(self, text: str) -> None:
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("1.0", text)
        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def _clear_textbox(self) -> None:
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
