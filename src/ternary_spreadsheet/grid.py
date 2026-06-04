"""Grid — an N×M sheet of ternary cells."""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from .cell import Cell, TernaryValue, _coerce


class Grid:
    """A rectangular grid of :class:`Cell` objects.

    Parameters
    ----------
    rows, cols : int
        Dimensions of the grid.  Must be >= 1.
    default : int or TernaryValue
        Initial value for every cell (default 0).
    """

    def __init__(self, rows: int, cols: int, default: int | TernaryValue = 0) -> None:
        if rows < 1 or cols < 1:
            raise ValueError("Grid dimensions must be >= 1")
        self._rows = rows
        self._cols = cols
        dv = _coerce(default)
        self._cells: List[List[Cell]] = [
            [Cell(dv) for _ in range(cols)] for _ in range(rows)
        ]

    # --- dimension helpers ---------------------------------------------------

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def shape(self) -> Tuple[int, int]:
        return (self._rows, self._cols)

    # --- cell access ---------------------------------------------------------

    def _check(self, r: int, c: int) -> None:
        if not (0 <= r < self._rows and 0 <= c < self._cols):
            raise IndexError(f"Cell ({r}, {c}) out of bounds for {self._rows}×{self._cols} grid")

    def get(self, r: int, c: int) -> Cell:
        """Return the cell at (*r*, *c*)."""
        self._check(r, c)
        return self._cells[r][c]

    def get_value(self, r: int, c: int) -> TernaryValue:
        """Shortcut: return the ternary value at (*r*, *c*)."""
        return self.get(r, c).value

    def set(self, r: int, c: int, value: int | TernaryValue) -> Cell:
        """Set the value at (*r*, *c*) and return the cell."""
        self._check(r, c)
        cell = self._cells[r][c]
        cell.value = value
        return cell

    def set_formula(self, r: int, c: int, formula: Callable[[], int]) -> Cell:
        """Attach a formula to cell (*r*, *c*)."""
        self._check(r, c)
        cell = self._cells[r][c]
        cell.formula = formula
        return cell

    # --- bulk operations -----------------------------------------------------

    def values(self) -> List[List[TernaryValue]]:
        """Return a plain list-of-lists of the current ternary values."""
        return [[c.value for c in row] for row in self._cells]

    def evaluate(self) -> "Grid":
        """Evaluate every cell that has a formula.  Returns *self* for chaining."""
        for row in self._cells:
            for cell in row:
                cell.evaluate()
        return self

    def reset(self) -> "Grid":
        """Mark all formula cells as stale."""
        for row in self._cells:
            for cell in row:
                cell.reset()
        return self

    def row(self, r: int) -> List[Cell]:
        """Return all cells in row *r*."""
        self._check(r, 0)
        return list(self._cells[r])

    def col(self, c: int) -> List[Cell]:
        """Return all cells in column *c*."""
        self._check(0, c)
        return [self._cells[r][c] for r in range(self._rows)]

    # --- dunder --------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Grid({self._rows}×{self._cols})"

    def __getitem__(self, key: Tuple[int, int]) -> Cell:
        r, c = key
        return self.get(r, c)
