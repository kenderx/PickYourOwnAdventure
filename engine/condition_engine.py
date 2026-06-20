"""
condition_engine.py
Evaluates Condition objects against the current game variable state.
"""
from __future__ import annotations

from typing import Any

from .story_model import Condition, ConditionOp


class ConditionEngine:
    """Evaluates whether story conditions are satisfied."""

    def evaluate(self, condition: Condition, variables: dict[str, Any]) -> bool:
        """
        Evaluate a single Condition.

        - "require" conditions: underlying op must be True.
        - "unless"  conditions: underlying op must be False.
        """
        result = self._evaluate_op(condition.op, variables)
        return (not result) if condition.type == "unless" else result

    def evaluate_all(
        self, conditions: list[Condition], variables: dict[str, Any]
    ) -> bool:
        """Return True only if *every* condition in the list passes."""
        return all(self.evaluate(c, variables) for c in conditions)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _evaluate_op(self, op: ConditionOp, variables: dict[str, Any]) -> bool:
        """Apply a comparison operator to a variable's current value."""
        if op.variable not in variables:
            # Unknown variables default to False (choice stays hidden)
            return False

        lhs = variables[op.variable]
        rhs = op.value

        try:
            if op.operator == "eq":
                return lhs == rhs
            elif op.operator == "ne":
                return lhs != rhs
            elif op.operator == "gt":
                return lhs > rhs
            elif op.operator == "lt":
                return lhs < rhs
            elif op.operator == "gte":
                return lhs >= rhs
            elif op.operator == "lte":
                return lhs <= rhs
        except TypeError:
            # e.g. comparing bool to int in unexpected ways
            return False

        return False
