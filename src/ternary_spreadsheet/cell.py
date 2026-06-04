"""Cell — the atomic unit of the ternary spreadsheet."""

from __future__ import annotations

from enum import IntEnum
from typing import Callable, Optional


class TernaryValue(IntEnum):
    """The three possible states of a ternary cell."""

    NEGATIVE = -1
    ZERO = 0
    POSITIVE = 1

    def __repr__(self) -> str:  # type: ignore[override]
        return f"TernaryValue({self.value:+d})"


# Acceptable raw values that coerce to TernaryValue
_VALID_RAW = {-1, 0, 1}


def _coerce(value: int | TernaryValue) -> TernaryValue:
    if isinstance(value, TernaryValue):
        return value
    if value in _VALID_RAW:
        return TernaryValue(value)
    raise ValueError(f"Invalid ternary value: {value!r} (must be -1, 0, or +1)")


class Cell:
    """A single spreadsheet cell with a ternary value.

    Parameters
    ----------
    value : int or TernaryValue, optional
        Static ternary value.  Defaults to 0.
    formula : callable, optional
        A zero-arg callable that returns a valid ternary value.
        When present the cell is *computed*; ``evaluate()`` runs the formula.
    """

    __slots__ = ("_value", "_formula", "_computed")

    def __init__(
        self,
        value: int | TernaryValue = 0,
        formula: Optional[Callable[[], int]] = None,
    ) -> None:
        self._value: TernaryValue = _coerce(value)
        self._formula = formula
        self._computed: bool = formula is None  # static cells are always computed

    # --- public API ----------------------------------------------------------

    @property
    def value(self) -> TernaryValue:
        return self._value

    @value.setter
    def value(self, v: int | TernaryValue) -> None:
        self._value = _coerce(v)
        self._formula = None  # setting a value clears formula
        self._computed = True

    @property
    def formula(self) -> Optional[Callable[[], int]]:
        return self._formula

    @formula.setter
    def formula(self, fn: Optional[Callable[[], int]]) -> None:
        self._formula = fn
        self._computed = fn is None

    @property
    def computed(self) -> bool:
        """True when the stored value is up-to-date (static or already evaluated)."""
        return self._computed

    def evaluate(self) -> TernaryValue:
        """Run the formula (if any) and update the stored value."""
        if self._formula is not None:
            self._value = _coerce(self._formula())
            self._computed = True
        return self._value

    def reset(self) -> None:
        """Mark cell as needing re-evaluation (clears computed flag)."""
        if self._formula is not None:
            self._computed = False

    # --- dunder helpers ------------------------------------------------------

    def __repr__(self) -> str:
        tag = " computed" if self._computed else " stale"
        form = " formula" if self._formula else ""
        return f"Cell({self._value:+d}{form}{tag})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Cell):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)
