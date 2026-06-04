"""Sort Engine — sort as natural selection.

Rows are treated as organisms; a fitness function scores each row,
and the engine sorts (or selects) rows based on fitness.
"""

from __future__ import annotations

from typing import Callable, List

from .grid import Grid


class SortEngine:
    """Sort rows of a :class:`Grid` by fitness.

    Parameters
    ----------
    grid : Grid
        The grid to operate on.
    fitness : callable
        A function that receives a list of cell values for a row and
        returns a numeric fitness score (higher is better).
    """

    def __init__(self, grid: Grid, fitness: Callable[[List[int]], float]) -> None:
        self.grid = grid
        self.fitness = fitness

    def score_row(self, r: int) -> float:
        """Compute the fitness score for row *r*."""
        values = [c.value for c in self.grid.row(r)]
        return self.fitness(values)

    def scores(self) -> List[float]:
        """Return fitness scores for every row."""
        return [self.score_row(r) for r in range(self.grid.rows)]

    def sort_ascending(self) -> List[int]:
        """Sort rows by fitness (lowest first).  Returns new row order."""
        order = list(range(self.grid.rows))
        order.sort(key=lambda r: self.score_row(r))
        self._reorder(order)
        return order

    def sort_descending(self) -> List[int]:
        """Sort rows by fitness (highest first).  Returns new row order."""
        order = list(range(self.grid.rows))
        order.sort(key=lambda r: self.score_row(r), reverse=True)
        self._reorder(order)
        return order

    def select_top(self, n: int) -> List[int]:
        """Return indices of the top *n* rows by fitness (highest first).

        Does **not** mutate the grid.
        """
        ranked = sorted(range(self.grid.rows), key=lambda r: self.score_row(r), reverse=True)
        return ranked[:n]

    def _reorder(self, order: List[int]) -> None:
        """Apply a row permutation to the underlying grid."""
        self.grid._cells = [self.grid._cells[i] for i in order]
