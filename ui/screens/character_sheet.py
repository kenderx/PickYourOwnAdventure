"""
character_sheet.py
Displays all visible story variables grouped by category.

Each variable is rendered according to its display_type:
    boolean  → ✓ / ✗  coloured badge
    bar      → progress bar with min/max labels
    number   → large numeric value
    auto     → infers from Python type
"""
from __future__ import annotations

import customtkinter as ctk


class CharacterSheetScreen(ctk.CTkFrame):
    """Full-screen character sheet showing all visible game variables."""

    def __init__(self, parent, app) -> None:
        c = app.colors
        super().__init__(parent, fg_color=c["bg_primary"], corner_radius=0)
        self.app = app
        self._return_to = "game"
        self._build_chrome()

    # ------------------------------------------------------------------
    # Static chrome (built once)
    # ------------------------------------------------------------------

    def _build_chrome(self) -> None:
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

        self._title_lbl = ctk.CTkLabel(
            top,
            text="Character Sheet",
            font=("Georgia", 17, "bold"),
            text_color=c["text_primary"],
        )
        self._title_lbl.pack(side="left", padx=10)

        # ---- Scrollable body (rebuilt each show) ----
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=c["bg_primary"],
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
        )
        self._scroll.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_show(self, return_to: str = "game", **kwargs) -> None:
        self._return_to = return_to
        self._rebuild()

    def _rebuild(self) -> None:
        """Clear and repopulate the scrollable body."""
        for widget in self._scroll.winfo_children():
            widget.destroy()

        gs = self.app.game_state
        if gs is None:
            self._no_game_label()
            return

        self._title_lbl.configure(
            text=f"Character Sheet  —  {gs.story.meta.title}"
        )

        # Group variables by category
        categories: dict[str, list] = {}
        for key, meta in gs.story.variables.items():
            if not meta.visible:
                continue
            cat = meta.category or "General"
            categories.setdefault(cat, []).append((key, meta))

        if not categories:
            self._no_game_label("No visible variables defined in this story.")
            return

        # Render each category
        inner = ctk.CTkFrame(self._scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=20)

        for cat_name, entries in categories.items():
            self._render_category(inner, cat_name, entries, gs.variables)

    # ------------------------------------------------------------------
    # Category section
    # ------------------------------------------------------------------

    def _render_category(
        self, parent, name: str, entries: list, live_vars: dict
    ) -> None:
        c = self.app.colors

        # Section heading
        ctk.CTkLabel(
            parent,
            text=name.upper(),
            font=("Segoe UI", 11, "bold"),
            text_color=c["accent"],
            anchor="w",
        ).pack(anchor="w", pady=(16, 4))

        ctk.CTkFrame(
            parent, fg_color=c["border"], height=1, corner_radius=0
        ).pack(fill="x", pady=(0, 10))

        # Card grid (2 columns)
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for idx, (key, meta) in enumerate(entries):
            row = idx // 2
            col = idx % 2
            value = live_vars.get(key, meta.value)
            card = self._make_card(grid, meta, value)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

    # ------------------------------------------------------------------
    # Variable card
    # ------------------------------------------------------------------

    def _make_card(self, parent, meta, value) -> ctk.CTkFrame:
        c = self.app.colors

        card = ctk.CTkFrame(
            parent,
            fg_color=c["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=c["border"],
        )

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        # Header row: icon + label
        head = ctk.CTkFrame(inner, fg_color="transparent")
        head.pack(fill="x")

        icon = meta.icon or self._default_icon(meta, value)
        ctk.CTkLabel(
            head,
            text=icon,
            font=("Segoe UI", 16),
            text_color=c["text_secondary"],
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            head,
            text=meta.label,
            font=("Segoe UI", 12, "bold"),
            text_color=c["text_secondary"],
            anchor="w",
        ).pack(side="left")

        # Value display
        display = meta.display_type
        if display == "auto":
            display = "boolean" if isinstance(value, bool) else "number"

        if display == "boolean":
            self._render_boolean(inner, value)
        elif display == "bar":
            self._render_bar(inner, value, meta)
        else:  # number or text
            self._render_number(inner, value)

        # Description tooltip
        if meta.description:
            ctk.CTkLabel(
                inner,
                text=meta.description,
                font=("Segoe UI", 10),
                text_color=c["text_muted"],
                wraplength=190,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(4, 0))

        return card

    def _render_boolean(self, parent, value: bool) -> None:
        c = self.app.colors
        if value:
            symbol = "✓"
            color  = c["success"]
            bg     = "#0d3d2b" if self.app.theme_name == "dark" else "#d1fae5"
        else:
            symbol = "✗"
            color  = c["text_muted"]
            bg     = c["bg_secondary"]

        badge = ctk.CTkFrame(
            parent, fg_color=bg, corner_radius=8, height=34
        )
        badge.pack(anchor="w", pady=(8, 0))
        badge.pack_propagate(False)

        ctk.CTkLabel(
            badge,
            text=f"  {symbol}  {'Acquired' if value else 'Not yet'}  ",
            font=("Segoe UI", 12, "bold"),
            text_color=color,
        ).pack(expand=True)

    def _render_bar(self, parent, value, meta) -> None:
        c = self.app.colors

        lo  = meta.min_value if meta.min_value is not None else 0
        hi  = meta.max_value if meta.max_value is not None else 10
        span = hi - lo
        if span == 0:
            ratio = 0.0
        else:
            ratio = max(0.0, min(1.0, (value - lo) / span))

        bar_color = c["bar_fill_low"] if ratio < 0.25 else c["bar_fill"]

        # Numeric label
        ctk.CTkLabel(
            parent,
            text=str(int(value)),
            font=("Segoe UI", 20, "bold"),
            text_color=bar_color,
        ).pack(anchor="w", pady=(6, 2))

        # Bar track + fill
        track = ctk.CTkFrame(
            parent, fg_color=c["bar_track"], corner_radius=4, height=10
        )
        track.pack(fill="x", pady=(0, 4))
        track.pack_propagate(False)
        track.update_idletasks()

        fill_width = max(0.0, min(1.0, ratio))
        fill = ctk.CTkFrame(
            track, fg_color=bar_color, corner_radius=4, height=10
        )
        # Use place for the fill so it respects ratio
        fill.place(relx=0, rely=0, relwidth=fill_width, relheight=1)

        # Min / max labels
        minmax = ctk.CTkFrame(parent, fg_color="transparent")
        minmax.pack(fill="x")
        ctk.CTkLabel(
            minmax, text=str(int(lo)),
            font=("Segoe UI", 9), text_color=c["text_muted"], anchor="w"
        ).pack(side="left")
        ctk.CTkLabel(
            minmax, text=str(int(hi)),
            font=("Segoe UI", 9), text_color=c["text_muted"], anchor="e"
        ).pack(side="right")

    def _render_number(self, parent, value) -> None:
        c = self.app.colors
        ctk.CTkLabel(
            parent,
            text=str(value),
            font=("Segoe UI", 26, "bold"),
            text_color=c["text_primary"],
        ).pack(anchor="w", pady=(8, 0))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _default_icon(self, meta, value) -> str:
        if isinstance(value, bool):
            return "✓" if value else "○"
        if isinstance(value, int):
            return "🔢"
        return "📌"

    def _no_game_label(self, text: str = "No active game.") -> None:
        c = self.app.colors
        ctk.CTkLabel(
            self._scroll,
            text=text,
            font=("Georgia", 14, "italic"),
            text_color=c["text_muted"],
        ).pack(pady=60)

    def _on_back(self) -> None:
        self.app.show_screen(self._return_to)

    # ------------------------------------------------------------------

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(fg_color=c["bg_primary"])
        self._scroll.configure(
            fg_color=c["bg_primary"],
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
        )
        self._rebuild()
