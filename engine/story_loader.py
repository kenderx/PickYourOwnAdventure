"""
story_loader.py
Parses a story.yaml file into a fully-typed Story object.
Provides clear authoring error messages for malformed stories.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from .story_model import (
    Choice, Condition, ConditionOp, Effect,
    Story, StoryMeta, StoryNode, VariableMeta,
)


class StoryLoadError(Exception):
    """Raised when a story.yaml file is malformed or references are invalid."""


class StoryLoader:
    """Loads and validates a story.yaml file."""

    def load(self, story_path: str) -> Story:
        """
        Parse *story_path* (path to story.yaml) and return a Story object.

        Raises StoryLoadError with a human-readable message on any problem.
        """
        path = Path(story_path)
        if not path.exists():
            raise StoryLoadError(f"Story file not found: {story_path}")

        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)

        if not isinstance(raw, dict):
            raise StoryLoadError(f"'{story_path}' is not a valid YAML mapping.")

        story_dir = path.parent

        meta = self._parse_meta(raw.get("meta", {}), story_dir)
        variables = self._parse_variables(raw.get("variables", {}))
        nodes = self._parse_nodes(raw.get("nodes", {}), story_dir)

        self._validate(meta, variables, nodes)

        return Story(meta=meta, variables=variables, nodes=nodes)

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def _parse_meta(self, data: dict, story_dir: Path) -> StoryMeta:
        for required in ("title", "start_node"):
            if required not in data:
                raise StoryLoadError(f"[meta] missing required field: '{required}'")

        cover = data.get("cover_image")
        if cover:
            cover_path = story_dir / cover
            cover = str(cover_path) if cover_path.exists() else None

        return StoryMeta(
            id=data.get("id", story_dir.name),
            title=data["title"],
            author=data.get("author", "Unknown"),
            version=str(data.get("version", "1.0")),
            description=data.get("description", ""),
            start_node=data["start_node"],
            cover_image=cover,
        )

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def _parse_variables(self, data: dict) -> dict[str, VariableMeta]:
        result: dict[str, VariableMeta] = {}

        for key, val in data.items():
            if isinstance(val, dict) and "value" in val:
                # Rich format: includes metadata
                meta = VariableMeta(
                    value=val["value"],
                    label=val.get("label", self._key_to_label(key)),
                    description=val.get("description", ""),
                    icon=val.get("icon", ""),
                    category=val.get("category", "General"),
                    visible=val.get("visible", True),
                    display_type=val.get("display_type", "auto"),
                    min_value=val.get("min_value"),
                    max_value=val.get("max_value"),
                )
            else:
                # Simple format: just a bare value
                meta = VariableMeta(
                    value=val,
                    label=self._key_to_label(key),
                )

            result[key] = meta

        return result

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def _parse_nodes(self, data: dict, story_dir: Path) -> dict[str, StoryNode]:
        nodes: dict[str, StoryNode] = {}

        for node_id, node_data in data.items():
            if not isinstance(node_data, dict):
                raise StoryLoadError(f"Node '{node_id}' must be a YAML mapping.")

            choices = [
                self._parse_choice(c, node_id, story_dir)
                for c in node_data.get("choices", [])
            ]

            node = StoryNode(
                id=node_id,
                title=node_data.get("title", ""),
                text=(node_data.get("text") or "").strip(),
                choices=choices,
                background=self._resolve_asset(node_data.get("background"), story_dir),
                music=self._resolve_asset(node_data.get("music"), story_dir),
                sfx=self._resolve_asset(node_data.get("sfx"), story_dir),
                is_ending=bool(node_data.get("ending", False)),
            )
            nodes[node_id] = node

        return nodes

    def _parse_choice(self, data: dict, node_id: str, story_dir: Path) -> Choice:
        if "text" not in data:
            raise StoryLoadError(
                f"A choice in node '{node_id}' is missing the required 'text' field."
            )
        next_node = data.get("next", "")
        conditions = self._parse_conditions(data.get("conditions", []), node_id)
        effects = self._parse_effects(data.get("effects", []), node_id)
        sfx = self._resolve_asset(data.get("sfx"), story_dir)
        return Choice(
            text=data["text"],
            next_node=next_node,
            conditions=conditions,
            effects=effects,
            sfx=sfx,
        )

    # ------------------------------------------------------------------
    # Conditions
    # ------------------------------------------------------------------

    def _parse_conditions(
        self, data: list, node_id: str
    ) -> list[Condition]:
        conditions: list[Condition] = []

        for item in data:
            if not isinstance(item, dict):
                raise StoryLoadError(
                    f"Node '{node_id}': each condition must be a mapping."
                )
            for cond_type in ("require", "unless"):
                if cond_type not in item:
                    continue
                var_dict = item[cond_type]
                if not isinstance(var_dict, dict):
                    raise StoryLoadError(
                        f"Node '{node_id}': condition '{cond_type}' value must be a mapping."
                    )
                for var_name, var_val in var_dict.items():
                    if isinstance(var_val, dict):
                        # Operator form: { variable: { gte: 2 } }
                        for op, threshold in var_val.items():
                            if op not in ("gte", "lte", "gt", "lt", "eq", "ne"):
                                raise StoryLoadError(
                                    f"Node '{node_id}': unknown condition operator '{op}'. "
                                    f"Valid operators: gte, lte, gt, lt, eq, ne"
                                )
                            conditions.append(
                                Condition(
                                    type=cond_type,
                                    op=ConditionOp(
                                        variable=var_name,
                                        operator=op,
                                        value=threshold,
                                    ),
                                )
                            )
                    else:
                        # Boolean shorthand: { has_lantern: true }
                        conditions.append(
                            Condition(
                                type=cond_type,
                                op=ConditionOp(
                                    variable=var_name,
                                    operator="eq",
                                    value=var_val,
                                ),
                            )
                        )

        return conditions

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------

    def _parse_effects(self, data: list, node_id: str) -> list[Effect]:
        effects: list[Effect] = []

        for item in data:
            if not isinstance(item, dict):
                raise StoryLoadError(
                    f"Node '{node_id}': each effect must be a mapping."
                )
            for effect_type, effect_data in item.items():
                if effect_type not in ("set", "increment", "decrement", "toggle"):
                    raise StoryLoadError(
                        f"Node '{node_id}': unknown effect type '{effect_type}'. "
                        f"Valid types: set, increment, decrement, toggle"
                    )

                if effect_type == "toggle":
                    # toggle: variable_name  OR  toggle: [var1, var2]
                    targets = (
                        effect_data if isinstance(effect_data, list) else [effect_data]
                    )
                    for var in targets:
                        effects.append(Effect(type="toggle", variable=str(var)))
                elif isinstance(effect_data, dict):
                    for var, val in effect_data.items():
                        effects.append(Effect(type=effect_type, variable=var, value=val))
                else:
                    raise StoryLoadError(
                        f"Node '{node_id}': effect '{effect_type}' must map to "
                        f"a variable: value dict."
                    )

        return effects

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(
        self,
        meta: StoryMeta,
        variables: dict[str, VariableMeta],
        nodes: dict[str, StoryNode],
    ) -> None:
        if meta.start_node not in nodes:
            raise StoryLoadError(
                f"[meta] start_node '{meta.start_node}' does not exist in nodes."
            )

        # Check all choice.next_node references exist
        for node_id, node in nodes.items():
            for choice in node.choices:
                if choice.next_node and choice.next_node not in nodes:
                    raise StoryLoadError(
                        f"Node '{node_id}', choice '{choice.text}': "
                        f"references unknown node '{choice.next_node}'."
                    )

        # Warn (but don't fail) for effects on unknown variables
        known_vars = set(variables.keys())
        for node_id, node in nodes.items():
            for choice in node.choices:
                for effect in choice.effects:
                    if effect.variable not in known_vars:
                        import warnings
                        warnings.warn(
                            f"Node '{node_id}', choice '{choice.text}': "
                            f"effect targets unknown variable '{effect.variable}'.",
                            stacklevel=2,
                        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key_to_label(key: str) -> str:
        """Convert 'snake_case_key' → 'Snake Case Key'."""
        return key.replace("_", " ").title()

    @staticmethod
    def _resolve_asset(filename: Optional[str], story_dir: Path) -> Optional[str]:
        """
        Resolve a relative asset filename to an absolute path.
        Returns None if *filename* is None or the resolved path does not exist.
        """
        if not filename:
            return None
        resolved = story_dir / filename
        return str(resolved) if resolved.exists() else None
