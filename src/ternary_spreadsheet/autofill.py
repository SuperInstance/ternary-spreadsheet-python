"""Autofill Engine — autofill as mutation.

Given a source range, the autofill engine copies values with optional
mutations (random flips) into a target range — simulating genetic drift.
"""

from __future__ import annotations

import random
from typing import Tuple

from .grid import Grid
from .cell import TernaryValue


class AutofillEngine:
    """Autofill a target region by copying (with optional mutation) from a source.

    Parameters
    ----------
    grid : Grid
        The grid to operate on.
    mutation_rate : float
        Probability [0, 1] that each copied value is randomly mutated.
    """

    def __init__(self, grid: Grid, mutation_rate: float = 0.1) -> None:
        self.grid = grid
        self.mutation_rate = max(0.0, min(1.0, mutation_rate))

    def _random_ternary(self) -> int:
        return random.choice([-1, 0, 1])

    def autofill(
        self,
        src: Tuple[int, int, int, int],
        dst: Tuple[int, int, int, int],
    ) -> None:
        """Copy the source rectangle into the destination with mutation.

        Both *src* and *dst* are ``(row_start, col_start, row_end, col_end)``
        tuples (inclusive bounds).  The destination rectangle is tiled with
        repeats of the source pattern.
        """
        sr, sc, er, ec = src
        dr, dc, der, dec = dst
        src_h = er - sr + 1
        src_w = ec - sc + 1

        for r in range(dr, der + 1):
            for c in range(dc, dec + 1):
                sr2 = sr + (r - dr) % src_h
                sc2 = sc + (c - dc) % src_w
                val = int(self.grid.get_value(sr2, sc2))
                if random.random() < self.mutation_rate:
                    val = self._random_ternary()
                self.grid.set(r, c, val)

    def autofill_row(self, src_row: int, dst_col_start: int, dst_col_end: int) -> None:
        """Autofill across a single row from the cell at *src_row*, column *dst_col_start*."""
        src_val = int(self.grid.get_value(src_row, dst_col_start))
        for c in range(dst_col_start, dst_col_end + 1):
            if c == dst_col_start:
                continue
            val = src_val
            if random.random() < self.mutation_rate:
                val = self._random_ternary()
            self.grid.set(src_row, c, val)

    def autofill_col(self, src_col: int, dst_row_start: int, dst_row_end: int) -> None:
        """Autofill down a single column from the cell at *dst_row_start*, *src_col*."""
        src_val = int(self.grid.get_value(dst_row_start, src_col))
        for r in range(dst_row_start, dst_row_end + 1):
            if r == dst_row_start:
                continue
            val = src_val
            if random.random() < self.mutation_rate:
                val = self._random_ternary()
            self.grid.set(r, src_col, val)
