"""
game_state.py
Runtime state of an active game session.
Owns the current node pointer, live variable values, and move history.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .story_model import Choice, Story, StoryNode
from .condition_engine import ConditionEngine
from .effect_engine import EffectEngine


@dataclass
class GameState:
    """
    Holds everything needed to represent a running game session.

    Create via GameState.new_game(story) for a fresh session,
    or GameState.from_dict(data, story) when loading a save.
    """
    story: Story
    current_node_id: str
    variables: dict[str, Any]
    history: list[str] = field(default_factory=list)

    # Private engines (excluded from repr / equality checks)
    _condition_engine: ConditionEngine = field(
        default_factory=ConditionEngine, repr=False, compare=False
    )
    _effect_engine: EffectEngine = field(
        default_factory=EffectEngine, repr=False, compare=False
    )

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def new_game(cls, story: Story) -> "GameState":
        """Start a brand-new session at the story's start node."""
        start = story.meta.start_node
        return cls(
            story=story,
            current_node_id=start,
            variables=story.get_initial_variables(),
            history=[start],
        )

    @classmethod
    def from_dict(cls, data: dict, story: Story) -> "GameState":
        """Restore a session from a previously serialised save dict."""
        return cls(
            story=story,
            current_node_id=data["current_node"],
            variables=data["variables"],
            history=data.get("history", [data["current_node"]]),
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def current_node(self) -> StoryNode:
        return self.story.nodes[self.current_node_id]

    def visible_choices(self) -> list[Choice]:
        """Return only the choices whose conditions are all satisfied."""
        node = self.current_node()
        return [
            choice
            for choice in node.choices
            if self._condition_engine.evaluate_all(choice.conditions, self.variables)
        ]

    def apply_choice(self, choice: Choice) -> None:
        """
        Apply the choice's effects to the variable state and advance the node pointer.
        Records the destination in history.
        """
        self._effect_engine.apply_all(choice.effects, self.variables)
        self.current_node_id = choice.next_node
        self.history.append(choice.next_node)

    # ------------------------------------------------------------------
    # Game-over check
    # ------------------------------------------------------------------

    def is_game_over(self) -> bool:
        """True when the current node is marked as an ending."""
        return self.current_node().is_ending

    # ------------------------------------------------------------------
    # Serialisation (for save/load)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise to a plain dict suitable for JSON storage."""
        node = self.current_node()
        return {
            "story_id": self.story.meta.id,
            "current_node": self.current_node_id,
            "chapter": node.title,
            "variables": dict(self.variables),   # shallow copy
            "history": list(self.history),
        }
