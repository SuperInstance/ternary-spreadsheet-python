"""Formulas — composable ternary functions for cells.

Every formula is a plain callable that returns an ``int`` in {-1, 0, +1}.
They are designed to be passed to :meth:`Grid.set_formula`.
"""

from __future__ import annotations

import random
from typing import Callable, List, Sequence


def _clamp(n: int) -> int:
    """Clamp an integer to the ternary range {-1, 0, +1}."""
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0


# ---------------------------------------------------------------------------
# SUM — sum the referenced values and clamp
# ---------------------------------------------------------------------------

def SUM(*getters: Callable[[], int]) -> Callable[[], int]:
    """Return a formula that sums the values from *getters* and clamps.

    Example::

        grid.set_formula(2, 0, SUM(lambda: grid.get_value(0, 0),
                                   lambda: grid.get_value(1, 0)))
    """
    def _formula() -> int:
        total = sum(g() for g in getters)
        return _clamp(total)
    return _formula


# ---------------------------------------------------------------------------
# PRODUCT — multiply the referenced values and clamp
# ---------------------------------------------------------------------------

def PRODUCT(*getters: Callable[[], int]) -> Callable[[], int]:
    """Return a formula that multiplies values from *getters* and clamps."""

    def _formula() -> int:
        result = 1
        for g in getters:
            result *= g()
        return _clamp(result)

    return _formula


# ---------------------------------------------------------------------------
# THRESHOLD — positive if sum >= threshold, negative if sum <= -threshold
# ---------------------------------------------------------------------------

def THRESHOLD(
    *getters: Callable[[], int],
    threshold: int = 1,
) -> Callable[[], int]:
    """Return +1 if sum >= *threshold*, -1 if sum <= -*threshold*, else 0."""

    def _formula() -> int:
        total = sum(g() for g in getters)
        if total >= threshold:
            return 1
        if total <= -threshold:
            return -1
        return 0

    return _formula


# ---------------------------------------------------------------------------
# EVOLVE — probabilistic evolution / drift toward a target
# ---------------------------------------------------------------------------

def EVOLVE(
    getter: Callable[[], int],
    target: int = 1,
    rate: float = 0.5,
) -> Callable[[], int]:
    """With probability *rate*, move *getter*'s value one step toward *target*.

    *rate* is clamped to [0, 1].  Movement is by ±1 per step.
    """

    def _formula() -> int:
        current = getter()
        if random.random() > rate:
            return current  # no mutation this tick
        if current < target:
            return min(current + 1, 1)
        if current > target:
            return max(current - 1, -1)
        return current  # already at target

    return _formula


# ---------------------------------------------------------------------------
# BEST — pick the maximum value from references
# ---------------------------------------------------------------------------

def BEST(*getters: Callable[[], int]) -> Callable[[], int]:
    """Return the maximum value among the *getters*."""

    def _formula() -> int:
        return max(g() for g in getters)

    return _formula
