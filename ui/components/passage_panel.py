"""
passage_panel.py
Scrollable story-text panel with a typewriter reveal animation.

The panel exposes:
    display(text)        — start typing *text* character-by-character
    skip_animation()     — jump to full text immediately
    clear()              — reset for a new node
"""
from __future__ import annotations

import os
import tkinter as tk
from typing import Optional

import customtkinter as ctk
from PIL import Image, ImageTk


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
        self._panel_image_obj = None          # keep reference to prevent GC
        self._panel_image_path: str | None = None
        self._bg_image_id: int | None = None
        self._text_id: int | None = None

        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        c = self.app.colors
        s = self.app.settings

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(
            self,
            bg=c["bg_panel"],
            highlightthickness=0,
        )
        self._canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self._scrollbar = ctk.CTkScrollbar(
            self,
            orientation="vertical",
            command=self._canvas.yview,
            fg_color=c["bg_panel"],
            button_color=c["scrollbar"],
            button_hover_color=c["accent_hover"],
        )
        self._scrollbar.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._text_id = self._canvas.create_text(
            8,
            8,
            anchor="nw",
            text="",
            fill=c["text_primary"],
            font=(self.app.settings.theme and "Georgia", s.font_size),
            width=max(1, self.winfo_width() - 24),
        )

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<Button-1>", lambda e: self.skip_animation())
        self.bind("<Button-1>", lambda e: self.skip_animation())
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)

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

    def set_panel_image(self, image_path: str | None) -> None:
        """Load and display a panel image behind the text."""
        self._panel_image_path = image_path

        if not image_path or not os.path.isfile(image_path):
            if self._bg_image_id is not None:
                self._canvas.delete(self._bg_image_id)
                self._bg_image_id = None
            self._panel_image_obj = None
            self._canvas.configure(bg=self.app.colors["bg_panel"])
            self._update_scroll_region()
            return

        try:
            self.update_idletasks()
            canvas_width = self._canvas.winfo_width()
            canvas_height = self._canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                self.after(50, lambda: self.set_panel_image(image_path))
                return

            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

            self._panel_image_obj = ImageTk.PhotoImage(pil_image)
            if self._bg_image_id is None:
                self._bg_image_id = self._canvas.create_image(
                    0,
                    0,
                    anchor="nw",
                    image=self._panel_image_obj,
                    tags="bg_image",
                )
            else:
                self._canvas.itemconfigure(self._bg_image_id, image=self._panel_image_obj)

            self._canvas.tag_lower(self._bg_image_id)
            self._canvas.configure(bg=self.app.colors["bg_panel"])
            self._update_scroll_region()
        except Exception as e:
            print(f"Error loading panel image '{image_path}': {e}")
            if self._bg_image_id is not None:
                self._canvas.delete(self._bg_image_id)
                self._bg_image_id = None
            self._panel_image_obj = None
            self._canvas.configure(bg=self.app.colors["bg_panel"])
            self._update_scroll_region()

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(
            fg_color=c["bg_panel"],
            border_color=c["border"],
        )
        self._canvas.configure(bg=c["bg_panel"])
        if self._text_id is not None:
            self._canvas.itemconfigure(
                self._text_id,
                fill=c["text_primary"],
                font=(self.app.settings.theme and "Georgia", self.app.settings.font_size),
            )
        self._update_scroll_region()

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
        if self._text_id is not None:
            self._canvas.itemconfigure(self._text_id, text=text)
            self._update_scroll_region()
            self._canvas.yview_moveto(0.0)

    def _clear_textbox(self) -> None:
        if self._text_id is not None:
            self._canvas.itemconfigure(self._text_id, text="")
            self._update_scroll_region()

    def _update_scroll_region(self) -> None:
        self._canvas.update_idletasks()
        bbox = self._canvas.bbox("all")
        if bbox:
            self._canvas.configure(scrollregion=(0, 0, bbox[2] + 8, bbox[3] + 8))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        if self._text_id is not None:
            new_width = max(1, event.width - 16)
            self._canvas.itemconfigure(self._text_id, width=new_width)
        if self._panel_image_path:
            self.set_panel_image(self._panel_image_path)
        else:
            self._update_scroll_region()

    def _on_mousewheel(self, event: tk.Event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
