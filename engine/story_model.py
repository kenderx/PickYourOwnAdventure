"""
story_model.py
Data classes representing a fully-parsed story and its components.
All engine logic operates on these types.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------

@dataclass
class ConditionOp:
    """
    A single comparison applied to a named variable.

    Operators: gte (>=), lte (<=), gt (>), lt (<), eq (==), ne (!=)
    For boolean variables, use eq: true / eq: false.
    """
    variable: str
    operator: str   # gte | lte | gt | lt | eq | ne
    value: Any


@dataclass
class Condition:
    """
    A condition controlling whether a choice is visible.

    type == "require"  → condition must be TRUE   to show the choice
    type == "unless"   → condition must be FALSE  to show the choice
    """
    type: str       # require | unless
    op: ConditionOp


# ---------------------------------------------------------------------------
# Effects
# ---------------------------------------------------------------------------

@dataclass
class Effect:
    """
    A mutation applied to game variables when a choice is selected.

    Types:
        set       → variable = value
        increment → variable += value
        decrement → variable -= value
        toggle    → variable = not variable   (value is unused)
    """
    type: str       # set | increment | decrement | toggle
    variable: str
    value: Any = None   # not used for toggle


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

@dataclass
class Choice:
    """A single selectable option inside a StoryNode."""
    text: str
    next_node: str
    conditions: list[Condition] = field(default_factory=list)
    effects: list[Effect] = field(default_factory=list)
    sfx: Optional[str] = None          # path to sound effect file


# ---------------------------------------------------------------------------
# Variable metadata
# ---------------------------------------------------------------------------

@dataclass
class VariableMeta:
    """
    Metadata for a story variable, used to render the Character Sheet.

    display_type:
        auto     → infer from Python type of value
        number   → plain integer/float with icon
        boolean  → check/cross mark with icon
        bar      → progress bar (requires min_value / max_value)
    """
    value: Any                          # initial value
    label: str = ""                     # human-readable name
    description: str = ""              # tooltip / flavour text
    icon: str = ""                     # emoji or symbol
    category: str = "General"          # groups on character sheet
    visible: bool = True               # show on character sheet
    display_type: str = "auto"         # auto | number | boolean | bar
    min_value: Optional[float] = None  # for bar display
    max_value: Optional[float] = None  # for bar display


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

@dataclass
class StoryNode:
    """A single scene / beat in the story."""
    id: str
    title: str
    text: str
    choices: list[Choice] = field(default_factory=list)
    background: Optional[str] = None   # absolute path to image file
    music: Optional[str] = None        # absolute path to music file
    sfx: Optional[str] = None          # absolute path to node-entry SFX
    is_ending: bool = False            # if True, no more choices offered


# ---------------------------------------------------------------------------
# Story metadata
# ---------------------------------------------------------------------------

@dataclass
class StoryMeta:
    """Top-level metadata about the story."""
    id: str
    title: str
    author: str
    start_node: str
    version: str = "1.0"
    description: str = ""
    cover_image: Optional[str] = None  # absolute path to cover image


# ---------------------------------------------------------------------------
# Story root
# ---------------------------------------------------------------------------

@dataclass
class Story:
    """The fully-parsed story, ready to be run by the engine."""
    meta: StoryMeta
    variables: dict[str, VariableMeta]  # key → metadata (incl. initial value)
    nodes: dict[str, StoryNode]         # node_id → node

    def get_initial_variables(self) -> dict[str, Any]:
        """Return a flat {key: initial_value} dict for GameState initialisation."""
        return {k: v.value for k, v in self.variables.items()}
