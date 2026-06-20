"""
effect_engine.py
Applies Effect objects to the mutable game variable dictionary.
"""
from __future__ import annotations

from typing import Any

from .story_model import Effect


class EffectEngine:
    """Applies story effects to the live game variables."""

    def apply(self, effect: Effect, variables: dict[str, Any]) -> None:
        """
        Apply a single Effect.

        Unknown variables are silently ignored (the loader already warns).
        """
        if effect.variable not in variables:
            return

        etype = effect.type

        if etype == "set":
            variables[effect.variable] = effect.value

        elif etype == "increment":
            try:
                variables[effect.variable] = variables[effect.variable] + effect.value
            except TypeError:
                pass  # guard against bad YAML values

        elif etype == "decrement":
            try:
                variables[effect.variable] = variables[effect.variable] - effect.value
            except TypeError:
                pass

        elif etype == "toggle":
            try:
                variables[effect.variable] = not variables[effect.variable]
            except TypeError:
                pass

    def apply_all(self, effects: list[Effect], variables: dict[str, Any]) -> None:
        """Apply a list of effects in order."""
        for effect in effects:
            self.apply(effect, variables)
