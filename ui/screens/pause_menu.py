"""
pause_menu.py
In-game pause overlay and load-from-main-menu screen.

Modes (set via on_show(mode=...)):
    "in_game"        — Resume / Save / Load / Main Menu
    "load_from_menu" — Load only (reached from main menu)
"""
from __future__ import annotations

from typing import Optional

import customtkinter as ctk

from engine.game_state import GameState
from engine.save_manager import NUM_SLOTS, SaveInfo
from engine.story_loader import StoryLoader


class PauseMenuScreen(ctk.CTkFrame):
    """Pause / save-load screen with a translucent overlay aesthetic."""

    def __init__(self, parent, app) -> None:
        c = app.colors
        super().__init__(parent, fg_color=c["bg_primary"], corner_radius=0)
        self.app = app
        self._mode = "in_game"
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        c = self.app.colors

        # Dark overlay that fills the screen
        self._overlay = ctk.CTkFrame(self, fg_color=c["bg_primary"], corner_radius=0)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Centred panel
        self._panel = ctk.CTkFrame(
            self._overlay,
            fg_color=c["bg_panel"],
            corner_radius=16,
            border_width=1,
            border_color=c["border_accent"],
            width=720,
        )
        self._panel.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        self._title_lbl = ctk.CTkLabel(
            self._panel,
            text="⏸  Paused",
            font=("Georgia", 22, "bold"),
            text_color=c["text_primary"],
        )
        self._title_lbl.pack(pady=(28, 4))

        ctk.CTkFrame(
            self._panel, fg_color=c["accent"], height=2, width=550, corner_radius=1
        ).pack(pady=(0, 18))

        # ---- Save slots ----
        self._slots_frame = ctk.CTkFrame(self._panel, fg_color="transparent")
        self._slots_frame.pack(fill="x", padx=28)

        self._slot_widgets: list = []  # rebuilt on show

        # ---- Action buttons ----
        btns = ctk.CTkFrame(self._panel, fg_color="transparent")
        btns.pack(fill="x", padx=28, pady=(20, 8))

        self._resume_btn = ctk.CTkButton(
            btns,
            text="←  Back",
            height=44,
            font=("Segoe UI", 13, "bold"),
            fg_color=c["btn_primary"],
            hover_color=c["btn_primary_h"],
            text_color="#ffffff",
            corner_radius=22,
            command=self._on_resume,
        )
        self._resume_btn.pack(fill="x", pady=5)

        self._menu_btn = ctk.CTkButton(
            btns,
            text="⌂  Main Menu",
            height=44,
            font=("Segoe UI", 13, "bold"),
            fg_color=c["btn_secondary"],
            hover_color=c["btn_secondary_h"],
            text_color=c["text_primary"],
            corner_radius=22,
            command=self._on_main_menu,
        )
        self._menu_btn.pack(fill="x", pady=5)

        ctk.CTkFrame(self._panel, fg_color="transparent", height=12).pack()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_show(self, mode: str = "in_game", **kwargs) -> None:
        self._mode = mode
        c = self.app.colors

        if mode == "in_game":
            self._title_lbl.configure(text="⏸  Paused")
            self._resume_btn.configure(text="←  Back")
            self._resume_btn.pack(fill="x", pady=5)
            self._menu_btn.configure(text="⌂  Main Menu")
            self._menu_btn.pack(fill="x", pady=5)
        else:  # load_from_menu
            self._title_lbl.configure(text="Load Game")
            self._resume_btn.pack_forget()
            self._menu_btn.configure(text="←  Back")

        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Reconstruct the slot widgets from current save data."""
        for w in self._slot_widgets:
            w.destroy()
        self._slot_widgets.clear()

        c = self.app.colors
        slots = self.app.save_mgr.get_all_slots()
        in_game = self._mode == "in_game"

        for i, info in enumerate(slots):
            slot_num = i + 1
            row = self._make_slot_row(slot_num, info, in_game)
            self._slot_widgets.append(row)

    def _make_slot_row(
        self, slot: int, info: Optional[SaveInfo], in_game: bool
    ) -> ctk.CTkFrame:
        c = self.app.colors

        row = ctk.CTkFrame(
            self._slots_frame,
            fg_color=c["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=c["border"],
            height=68,
        )
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=6)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, minsize=240)

        # Slot label + info
        label_frame = ctk.CTkFrame(inner, fg_color="transparent")
        label_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            label_frame,
            text=f"Slot {slot}",
            font=("Segoe UI", 11, "bold"),
            text_color=c["text_secondary"],
        ).pack(anchor="w")

        if info:
            ctk.CTkLabel(
                label_frame,
                text=f"{info.story_title}  ·  {info.chapter}",
                font=("Georgia", 11, "italic"),
                text_color=c["text_muted"],
            ).pack(anchor="w")
            ctk.CTkLabel(
                label_frame,
                text=info.timestamp,
                font=("Segoe UI", 10),
                text_color=c["text_muted"],
            ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                label_frame,
                text="— Empty —",
                font=("Segoe UI", 11, "italic"),
                text_color=c["text_muted"],
            ).pack(anchor="w", pady=4)

        # Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=(12, 0))

        small_btn = dict(
            width=116, height=34,
            font=("Segoe UI", 11, "bold"),
            corner_radius=15,
        )

        if in_game:
            ctk.CTkButton(
                btn_frame,
                text="Save",
                fg_color=c["success"],
                hover_color="#0d9e6e",
                text_color="#ffffff",
                command=lambda s=slot: self._on_save(s),
                **small_btn,
            ).pack(side="left", padx=(0, 4), pady=(11, 11))

        if info:
            ctk.CTkButton(
                btn_frame,
                text="Load",
                fg_color=c["btn_primary"],
                hover_color=c["btn_primary_h"],
                text_color="#ffffff",
                command=lambda s=slot, raw=info.raw: self._on_load(s, raw),
                **small_btn,
            ).pack(side="left", padx=(0, 4), pady=(11, 11))

        return row

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_resume(self) -> None:
        self.app.audio.resume_music()
        self.app.show_screen("game")

    def _on_main_menu(self) -> None:
        self.app.audio.stop_music()
        self.app.game_state = None
        self.app.show_screen("main_menu")

    def _on_save(self, slot: int) -> None:
        if self.app.game_state and self.app.story_path:
            self.app.save_mgr.save(slot, self.app.game_state, self.app.story_path)
            self._rebuild_slots()

    def _on_load(self, slot: int, raw: dict) -> None:
        story_path = raw.get("story_path", "")
        if not story_path:
            return
        try:
            loader = StoryLoader()
            story = loader.load(story_path)
            self.app.story_path = story_path
            self.app.game_state = GameState.from_dict(raw, story)
            self.app.show_screen("game")
        except Exception as exc:
            # Show error inline
            self._title_lbl.configure(
                text=f"Load failed: {exc}",
                text_color=self.app.colors["danger"],
            )

    # ------------------------------------------------------------------

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_primary"])
        self._overlay.configure(fg_color=c["bg_primary"])
        self._panel.configure(
            fg_color=c["bg_panel"], border_color=c["border_accent"]
        )
        self._title_lbl.configure(text_color=c["text_primary"])
        self._resume_btn.configure(
            fg_color=c["btn_primary"], hover_color=c["btn_primary_h"]
        )
        self._menu_btn.configure(
            fg_color=c["btn_secondary"],
            hover_color=c["btn_secondary_h"],
            text_color=c["text_primary"],
        )
        self._rebuild_slots()
