"""
choice_panel.py
Dynamic panel that displays the visible choices for the current node.

Choices are rebuilt entirely on each call to display_choices().
Each button fires the on_choice_selected callback and plays its SFX.
"""
from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from engine.story_model import Choice

# Unicode circled numbers for choice prefixes ①②③…
CIRCLE_NUMS = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]


class ChoicePanel(ctk.CTkScrollableFrame):
    """
    Scrollable frame containing one button per visible choice.
    Pass on_choice_selected to receive the chosen Choice object.
    """

    def __init__(self, parent, app, on_choice_selected: Callable[[Choice], None], **kwargs) -> None:
        c = app.colors
        super().__init__(
            parent,
            fg_color=c["bg_secondary"],
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
            corner_radius=0,
            **kwargs,
        )
        self.app = app
        self._callback = on_choice_selected
        self._buttons: list[ctk.CTkButton] = []
        self._choices: list[Choice] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def display_choices(self, choices: list[Choice], is_ending: bool = False) -> None:
        """Rebuild buttons for *choices*."""
        self._clear()
        self._choices = choices

        if is_ending:
            self._add_ending_label()
            return

        if not choices:
            self._add_no_choices_label()
            return

        for idx, choice in enumerate(choices):
            self._add_choice_button(idx, choice)

    def clear(self) -> None:
        self._clear()

    def apply_theme(self) -> None:
        c = self.app.colors
        self.configure(
            fg_color=c["bg_secondary"],
            scrollbar_button_color=c["scrollbar"],
            scrollbar_button_hover_color=c["accent_hover"],
        )
        # Rebuild with current choices so colours update
        if self._choices:
            self.display_choices(self._choices)

    # ------------------------------------------------------------------
    # Internal builders
    # ------------------------------------------------------------------

    def _add_choice_button(self, idx: int, choice: Choice) -> None:
        c = self.app.colors

        prefix = CIRCLE_NUMS[idx] if idx < len(CIRCLE_NUMS) else f"{idx + 1}."
        label  = f"  {prefix}  {choice.text}"

        btn = ctk.CTkButton(
            self,
            text=label,
            anchor="w",
            height=52,
            font=("Segoe UI", 13),
            fg_color=c["choice_bg"],
            hover_color=c["choice_hover"],
            text_color=c["text_primary"],
            border_color=c["choice_border"],
            border_width=1,
            corner_radius=8,
            command=lambda ch=choice: self._on_click(ch),
        )
        btn.pack(fill="x", padx=12, pady=(6, 0))
        self._buttons.append(btn)

    def _add_ending_label(self) -> None:
        c = self.app.colors
        lbl = ctk.CTkLabel(
            self,
            text="— The End —",
            font=("Georgia", 15, "italic"),
            text_color=c["text_accent"],
        )
        lbl.pack(pady=20)
        self._buttons.append(lbl)

    def _add_no_choices_label(self) -> None:
        c = self.app.colors
        lbl = ctk.CTkLabel(
            self,
            text="No available choices.",
            font=("Segoe UI", 12),
            text_color=c["text_muted"],
        )
        lbl.pack(pady=16)
        self._buttons.append(lbl)

    def _on_click(self, choice: Choice) -> None:
        if choice.sfx:
            self.app.audio.play_sfx(choice.sfx)
        self._callback(choice)

    def _clear(self) -> None:
        for widget in self._buttons:
            widget.destroy()
        self._buttons.clear()
