"""
main_menu.py
The title / landing screen shown on launch.
Features an animated gradient shimmer behind the title and styled nav buttons.
"""
from __future__ import annotations

import math
import tkinter as tk

import customtkinter as ctk


class MainMenuScreen(ctk.CTkFrame):
    """Animated title screen with New Game / Load / Settings / Quit."""

    def __init__(self, parent, app) -> None:
        c = app.colors
        super().__init__(parent, fg_color=c["bg_primary"], corner_radius=0)
        self.app = app
        self._anim_id = None
        self._anim_offset = 0.0
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        c = self.app.colors

        # ---- Background canvas (animated gradient) ----
        self._canvas = tk.Canvas(
            self, bg=c["bg_primary"], highlightthickness=0
        )
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._canvas.bind("<Configure>", self._on_canvas_resize)

        # ---- Content frame (centred) ----
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # ---- Decorative top rule ----
        rule_top = ctk.CTkFrame(
            content, fg_color=c["accent"], height=2, width=320, corner_radius=1
        )
        rule_top.pack(pady=(0, 18))

        # ---- Title ----
        ctk.CTkLabel(
            content,
            text="PICK YOUR OWN",
            font=("Georgia", 38, "bold"),
            text_color=c["text_primary"],
        ).pack()

        ctk.CTkLabel(
            content,
            text="ADVENTURE",
            font=("Georgia", 52, "bold"),
            text_color=c["accent"],
        ).pack()

        ctk.CTkLabel(
            content,
            text="Your story. Your choices. Your destiny.",
            font=("Georgia", 14, "italic"),
            text_color=c["text_secondary"],
        ).pack(pady=(8, 0))

        # ---- Decorative bottom rule ----
        rule_bot = ctk.CTkFrame(
            content, fg_color=c["accent"], height=2, width=320, corner_radius=1
        )
        rule_bot.pack(pady=(18, 36))

        # ---- Buttons ----
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack()

        self._new_btn = self._make_btn(
            btn_frame, "✦  New Game", self._on_new_game, primary=True
        )
        self._load_btn = self._make_btn(
            btn_frame, "⟳  Load Game", self._on_load_game, primary=False
        )
        self._settings_btn = self._make_btn(
            btn_frame, "⚙  Settings", self._on_settings, primary=False
        )
        self._quit_btn = self._make_btn(
            btn_frame, "✕  Quit", self._on_quit, primary=False, danger=True
        )

        # ---- Version stamp ----
        ctk.CTkLabel(
            self,
            text="v1.0",
            font=("Segoe UI", 10),
            text_color=c["text_muted"],
        ).place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-8)

    def _make_btn(
        self,
        parent,
        text: str,
        command,
        primary: bool = False,
        danger: bool = False,
    ) -> ctk.CTkButton:
        c = self.app.colors
        if primary:
            fg  = c["btn_primary"]
            hov = c["btn_primary_h"]
        elif danger:
            fg  = c["btn_danger"]
            hov = c["btn_danger_h"]
        else:
            fg  = c["btn_secondary"]
            hov = c["btn_secondary_h"]

        btn = ctk.CTkButton(
            parent,
            text=text,
            width=260,
            height=52,
            font=("Segoe UI", 14, "bold"),
            fg_color=fg,
            hover_color=hov,
            text_color=c["text_primary"],
            corner_radius=26,
            command=command,
        )
        btn.pack(pady=7)
        return btn

    # ------------------------------------------------------------------
    # Animation — a slow drifting glow oval on the canvas
    # ------------------------------------------------------------------

    def _on_canvas_resize(self, event=None) -> None:
        self._redraw_bg()

    def _redraw_bg(self, offset: float = 0.0) -> None:
        c   = self._canvas
        w   = c.winfo_width()
        h   = c.winfo_height()
        if w < 2 or h < 2:
            return
        c.delete("bg")
        bg = self.app.colors["bg_primary"]
        c.create_rectangle(0, 0, w, h, fill=bg, outline="", tags="bg")

        # Drift the glow with offset
        cx = w * 0.5 + math.sin(offset) * w * 0.12
        cy = h * 0.38 + math.cos(offset * 0.7) * h * 0.06
        rx, ry = w * 0.38, h * 0.30

        # Draw several concentric ovals fading from accent → transparent
        accent_hex = self.app.colors["accent"]
        r = int(accent_hex[1:3], 16)
        g = int(accent_hex[3:5], 16)
        b = int(accent_hex[5:7], 16)

        steps = 18
        for i in range(steps, 0, -1):
            alpha = int(9 * (i / steps))           # 0–9 (hex digit)
            color = f"#{r:02x}{g:02x}{b:02x}{alpha:1x}{alpha:1x}"
            # tkinter doesn't support alpha in create_oval; use stipple trick
            factor = i / steps
            c.create_oval(
                cx - rx * factor,
                cy - ry * factor,
                cx + rx * factor,
                cy + ry * factor,
                fill=self.app.colors["bg_primary"],
                outline="",
                tags="bg",
            )
        # One visible soft oval at the centre
        glow_color = self.app.colors["accent_dark"]
        c.create_oval(
            cx - rx * 0.45, cy - ry * 0.45,
            cx + rx * 0.45, cy + ry * 0.45,
            fill=glow_color, outline="", tags="bg",
        )
        c.tag_lower("bg")

    def _start_animation(self) -> None:
        self._anim_offset = 0.0
        self._animate()

    def _animate(self) -> None:
        self._anim_offset += 0.015
        self._redraw_bg(self._anim_offset)
        self._anim_id = self.after(40, self._animate)

    def _stop_animation(self) -> None:
        if self._anim_id:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_show(self, **kwargs) -> None:
        # Refresh Load button state
        has_save = self.app.save_mgr.has_any_save()
        self._load_btn.configure(
            state="normal" if has_save else "disabled",
            text_color=self.app.colors["text_primary"] if has_save else self.app.colors["text_muted"],
        )
        self._start_animation()

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_primary"])
        # Simpler than rebuilding — just update colours
        self._redraw_bg(self._anim_offset)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _on_new_game(self) -> None:
        self._stop_animation()
        self.app.show_screen("story_select")

    def _on_load_game(self) -> None:
        self._stop_animation()
        self.app.show_screen("pause", mode="load_from_menu")

    def _on_settings(self) -> None:
        self._stop_animation()
        self.app.show_screen("settings", return_to="main_menu")

    def _on_quit(self) -> None:
        self.app._on_close()
