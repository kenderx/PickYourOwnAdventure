"""
status_bar.py
Thin top bar in the game screen: shows chapter title and icon buttons
for the Pause menu and Character Sheet.
"""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """
    Fixed-height header bar displayed above the passage panel.

    Displays:
        left  — chapter title (italic, story font)
        right — ☰ Menu  and  📋 Sheet  icon buttons
    """

    def __init__(
        self,
        parent,
        app,
        on_menu: Callable,
        on_character_sheet: Callable,
        **kwargs,
    ) -> None:
        c = app.colors
        super().__init__(
            parent,
            fg_color=c["bg_secondary"],
            corner_radius=0,
            height=46,
            **kwargs,
        )
        self.app = app
        self.pack_propagate(False)
        self._build(on_menu, on_character_sheet)

    # ------------------------------------------------------------------

    def _build(self, on_menu: Callable, on_character_sheet: Callable) -> None:
        c = self.app.colors

        # Story title (far left)
        self._story_title_lbl = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 11),
            text_color=c["text_muted"],
            anchor="w",
        )
        self._story_title_lbl.pack(side="left", padx=(14, 4), pady=4)

        # Separator
        sep = ctk.CTkLabel(self, text="›", text_color=c["text_muted"], font=("Segoe UI", 11))
        sep.pack(side="left", padx=0)

        # Chapter title
        self._chapter_lbl = ctk.CTkLabel(
            self,
            text="",
            font=("Georgia", 13, "italic"),
            text_color=c["text_accent"],
            anchor="w",
        )
        self._chapter_lbl.pack(side="left", padx=(4, 12), pady=4)

        # Right-side buttons
        btn_cfg = dict(
            width=38,
            height=32,
            corner_radius=8,
            fg_color=c["bg_card"],
            hover_color=c["choice_hover"],
            text_color=c["text_secondary"],
            font=("Segoe UI", 14),
        )

        self._sheet_btn = ctk.CTkButton(
            self, text="📋", command=on_character_sheet, **btn_cfg
        )
        self._sheet_btn.pack(side="right", padx=(4, 12), pady=6)

        self._menu_btn = ctk.CTkButton(
            self, text="☰", command=on_menu, **btn_cfg
        )
        self._menu_btn.pack(side="right", padx=(4, 2), pady=6)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_node(self, story_title: str, chapter_title: str) -> None:
        self._story_title_lbl.configure(text=story_title)
        self._chapter_lbl.configure(text=chapter_title)

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_secondary"])
        self._story_title_lbl.configure(text_color=c["text_muted"])
        self._chapter_lbl.configure(text_color=c["text_accent"])
        for btn in (self._menu_btn, self._sheet_btn):
            btn.configure(
                fg_color=c["bg_card"],
                hover_color=c["choice_hover"],
                text_color=c["text_secondary"],
            )
