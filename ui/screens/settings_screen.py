"""
settings_screen.py
User preferences panel: theme, font size, text speed, and volume sliders.
Changes take effect immediately; saved on "Back".
"""
from __future__ import annotations

import customtkinter as ctk


class SettingsScreen(ctk.CTkFrame):
    """Settings panel reachable from both the main menu and pause menu."""

    def __init__(self, parent, app) -> None:
        c = app.colors
        super().__init__(parent, fg_color=c["bg_primary"], corner_radius=0)
        self.app = app
        self._return_to = "main_menu"
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
            command=self._on_back,
        ).pack(side="left", padx=14, pady=10)

        ctk.CTkLabel(
            top,
            text="Settings",
            font=("Georgia", 17, "bold"),
            text_color=c["text_primary"],
        ).pack(side="left", padx=10)

        # ---- Scrollable body ----
        body = ctk.CTkScrollableFrame(
            self,
            fg_color=c["bg_primary"],
            scrollbar_button_color=c["scrollbar"],
        )
        body.pack(fill="both", expand=True, padx=0, pady=0)

        inner = ctk.CTkFrame(body, fg_color="transparent")
        inner.pack(padx=80, pady=30, fill="both")

        s = self.app.settings

        # ---- Theme ----
        self._section(inner, "🎨  Appearance")

        theme_row = ctk.CTkFrame(inner, fg_color="transparent")
        theme_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            theme_row, text="Theme", font=("Segoe UI", 13),
            text_color=c["text_secondary"], width=160, anchor="w"
        ).pack(side="left")

        self._theme_var = ctk.StringVar(value=s.theme)
        for name in ("dark", "light", "sepia"):
            ctk.CTkRadioButton(
                theme_row,
                text=name.capitalize(),
                variable=self._theme_var,
                value=name,
                font=("Segoe UI", 13),
                text_color=c["text_primary"],
                fg_color=c["accent"],
                hover_color=c["accent_hover"],
                command=self._on_theme_change,
            ).pack(side="left", padx=12)

        # ---- Font size ----
        self._section(inner, "🔤  Reading")

        self._font_size_var = ctk.IntVar(value=s.font_size)
        self._slider_row(
            inner,
            label="Font Size",
            variable=self._font_size_var,
            from_=10, to=24, steps=14,
            fmt=lambda v: f"{int(v)} pt",
            command=self._on_font_size,
        )

        self._text_speed_var = ctk.DoubleVar(value=s.text_speed)
        self._slider_row(
            inner,
            label="Text Speed",
            variable=self._text_speed_var,
            from_=5, to=100, steps=95,
            fmt=lambda v: ("Instant" if v >= 100 else f"{int(v)} ch/s"),
            command=self._on_text_speed,
        )

        # ---- Audio ----
        self._section(inner, "🔊  Audio")

        self._music_var = ctk.DoubleVar(value=s.music_volume)
        self._slider_row(
            inner,
            label="Music Volume",
            variable=self._music_var,
            from_=0.0, to=1.0, steps=100,
            fmt=lambda v: f"{int(v * 100)}%",
            command=self._on_music_volume,
        )

        self._sfx_var = ctk.DoubleVar(value=s.sfx_volume)
        self._slider_row(
            inner,
            label="SFX Volume",
            variable=self._sfx_var,
            from_=0.0, to=1.0, steps=100,
            fmt=lambda v: f"{int(v * 100)}%",
            command=self._on_sfx_volume,
        )

    # ------------------------------------------------------------------
    # Row builders
    # ------------------------------------------------------------------

    def _section(self, parent, title: str) -> None:
        c = self.app.colors
        ctk.CTkLabel(
            parent,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=c["accent"],
            anchor="w",
        ).pack(anchor="w", pady=(22, 6))
        ctk.CTkFrame(
            parent, fg_color=c["border"], height=1, corner_radius=0
        ).pack(fill="x", pady=(0, 10))

    def _slider_row(
        self, parent, label: str, variable, from_, to, steps, fmt, command
    ) -> None:
        c = self.app.colors

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=6)

        ctk.CTkLabel(
            row, text=label, font=("Segoe UI", 13),
            text_color=c["text_secondary"], width=160, anchor="w"
        ).pack(side="left")

        value_lbl = ctk.CTkLabel(
            row, text=fmt(variable.get()),
            font=("Segoe UI", 12, "bold"),
            text_color=c["text_accent"], width=70, anchor="e"
        )
        value_lbl.pack(side="right")

        def on_slide(val):
            variable.set(val)
            value_lbl.configure(text=fmt(val))
            command(val)

        slider = ctk.CTkSlider(
            row,
            variable=variable,
            from_=from_, to=to,
            number_of_steps=steps,
            fg_color=c["bar_track"],
            progress_color=c["accent"],
            button_color=c["accent"],
            button_hover_color=c["accent_hover"],
            command=on_slide,
        )
        slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_theme_change(self) -> None:
        self.app.apply_theme(self._theme_var.get())

    def _on_font_size(self, val) -> None:
        self.app.settings.font_size = int(val)

    def _on_text_speed(self, val) -> None:
        self.app.settings.text_speed = int(val)

    def _on_music_volume(self, val) -> None:
        self.app.settings.music_volume = float(val)
        self.app.audio.music_volume = float(val)

    def _on_sfx_volume(self, val) -> None:
        self.app.settings.sfx_volume = float(val)
        self.app.audio.sfx_volume = float(val)

    def _on_back(self) -> None:
        self.app.settings_mgr.save()
        self.app.show_screen(self._return_to)

    # ------------------------------------------------------------------

    def on_show(self, return_to: str = "main_menu", **kwargs) -> None:
        self._return_to = return_to

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_primary"])
