"""Ternary Spreadsheet — cells that are tiny ternary agents."""

from .cell import Cell, TernaryValue
from .grid import Grid
from .formula import SUM, PRODUCT, THRESHOLD, EVOLVE, BEST
from .sort_engine import SortEngine
from .autofill import AutofillEngine

__all__ = [
    "Cell",
    "TernaryValue",
    "Grid",
    "SUM",
    "PRODUCT",
    "THRESHOLD",
    "EVOLVE",
    "BEST",
    "SortEngine",
    "AutofillEngine",
]
