"""
story_select.py
Story browser screen.  Scans the /stories/ directory for story.yaml files
and displays each as a card (cover art + title + author + description).
"""
from __future__ import annotations

import os
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from engine.story_loader import StoryLoader, StoryLoadError
from engine.game_state import GameState
from utils import find_stories_dir


class StorySelectScreen(ctk.CTkFrame):
    """Grid of story cards; click one to start a new game."""

    def __init__(self, parent, app) -> None:
        c = app.colors
        super().__init__(parent, fg_color=c["bg_primary"], corner_radius=0)
        self.app = app
        self._loader = StoryLoader()
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        c = self.app.colors

        # ---- Top bar ----
        top = ctk.CTkFrame(self, fg_color=c["bg_secondary"], corner_radius=0, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkButton(
            top,
            text="← Back",
            width=90,
            height=34,
            font=("Segoe UI", 13),
            fg_color=c["btn_secondary"],
            hover_color=c["btn_secondary_h"],
            text_color=c["text_primary"],
            corner_radius=8,
            command=lambda: self.app.show_screen("main_menu"),
        ).pack(side="left", padx=14, pady=10)

        ctk.CTkLabel(
            top,
            text="Select Your Story",
            font=("Georgia", 17, "bold"),
            text_color=c["text_primary"],
        ).pack(side="left", padx=10)

        # ---- Scrollable card area ----
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=c["bg_primary"],
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
        )
        self._scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # ---- Error / empty label (hidden by default) ----
        self._empty_lbl = ctk.CTkLabel(
            self._scroll,
            text="No stories found.\nPlace story folders in the 'stories/' directory.",
            font=("Georgia", 14, "italic"),
            text_color=c["text_muted"],
            justify="center",
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_show(self, **kwargs) -> None:
        self._refresh_stories()

    def _refresh_stories(self) -> None:
        """Re-scan the stories directory and rebuild cards."""
        # Clear previous cards
        for widget in self._scroll.winfo_children():
            widget.destroy()

        stories_dir = Path(find_stories_dir())
        if not stories_dir.exists():
            self._show_empty("Stories directory not found.")
            return

        story_files = sorted(stories_dir.rglob("story.yaml"))
        if not story_files:
            self._show_empty("No stories found.\nAdd story folders to the 'stories/' directory.")
            return

        for story_path in story_files:
            self._add_story_card(story_path)

    def _show_empty(self, text: str) -> None:
        c = self.app.colors
        ctk.CTkLabel(
            self._scroll,
            text=text,
            font=("Georgia", 14, "italic"),
            text_color=c["text_muted"],
            justify="center",
        ).pack(pady=60)

    # ------------------------------------------------------------------
    # Story cards
    # ------------------------------------------------------------------

    def _add_story_card(self, story_path: Path) -> None:
        c = self.app.colors

        # Quick-load just the meta (full parse happens on click)
        try:
            story = self._loader.load(str(story_path))
            meta = story.meta
        except StoryLoadError as exc:
            self._add_error_card(story_path, str(exc))
            return

        card = ctk.CTkFrame(
            self._scroll,
            fg_color=c["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=c["border"],
        )
        card.pack(fill="x", padx=24, pady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        # Cover image (left)
        if meta.cover_image and os.path.isfile(meta.cover_image):
            try:
                img = Image.open(meta.cover_image).resize((120, 90))
                photo = ctk.CTkImage(img, size=(120, 90))
                cover_lbl = ctk.CTkLabel(inner, image=photo, text="")
                cover_lbl.image = photo
                cover_lbl.pack(side="left", padx=(0, 16))
            except Exception:
                self._add_placeholder_cover(inner)
        else:
            self._add_placeholder_cover(inner)

        # Text block (right)
        text_frame = ctk.CTkFrame(inner, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            text_frame,
            text=meta.title,
            font=("Georgia", 18, "bold"),
            text_color=c["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text=f"by {meta.author}",
            font=("Georgia", 12, "italic"),
            text_color=c["text_secondary"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 6))

        if meta.description:
            ctk.CTkLabel(
                text_frame,
                text=meta.description,
                font=("Segoe UI", 12),
                text_color=c["text_muted"],
                anchor="w",
                wraplength=460,
                justify="left",
            ).pack(anchor="w")

        # Play button
        ctk.CTkButton(
            text_frame,
            text="▶  Begin Adventure",
            width=180,
            height=36,
            font=("Segoe UI", 13, "bold"),
            fg_color=c["btn_primary"],
            hover_color=c["btn_primary_h"],
            text_color="#ffffff",
            corner_radius=18,
            command=lambda sp=str(story_path), s=story: self._start_story(sp, s),
        ).pack(anchor="w", pady=(10, 0))

    def _add_placeholder_cover(self, parent) -> None:
        c = self.app.colors
        ph = ctk.CTkFrame(
            parent,
            width=120, height=90,
            fg_color=c["bg_secondary"],
            corner_radius=8,
        )
        ph.pack(side="left", padx=(0, 16))
        ph.pack_propagate(False)
        ctk.CTkLabel(
            ph, text="📖", font=("Segoe UI", 32), text_color=c["text_muted"]
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _add_error_card(self, story_path: Path, error: str) -> None:
        c = self.app.colors
        card = ctk.CTkFrame(
            self._scroll,
            fg_color=c["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=c["danger"],
        )
        card.pack(fill="x", padx=24, pady=10)
        ctk.CTkLabel(
            card,
            text=f"⚠ Failed to load: {story_path.parent.name}\n{error}",
            font=("Segoe UI", 12),
            text_color=c["danger"],
            justify="left",
        ).pack(padx=16, pady=12)

    # ------------------------------------------------------------------
    # Start a story
    # ------------------------------------------------------------------

    def _start_story(self, story_path: str, story) -> None:
        self.app.story_path = story_path
        self.app.game_state = GameState.new_game(story)
        self.app.show_screen("game")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_primary"])
        self._refresh_stories()
