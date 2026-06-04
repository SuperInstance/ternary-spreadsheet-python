"""Tests for the ternary spreadsheet engine."""

import random
import pytest

from ternary_spreadsheet import (
    Cell,
    TernaryValue,
    Grid,
    SUM,
    PRODUCT,
    THRESHOLD,
    EVOLVE,
    BEST,
    SortEngine,
    AutofillEngine,
)


# ── Cell tests ────────────────────────────────────────────────────────────

class TestCell:
    def test_default_value_is_zero(self):
        c = Cell()
        assert c.value == TernaryValue.ZERO
        assert c.computed is True

    def test_explicit_positive(self):
        c = Cell(1)
        assert c.value == TernaryValue.POSITIVE

    def test_explicit_negative(self):
        c = Cell(-1)
        assert c.value == TernaryValue.NEGATIVE

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError, match="Invalid ternary value"):
            Cell(2)

    def test_setter_coerces_and_clears_formula(self):
        c = Cell(formula=lambda: 1)
        assert c.formula is not None
        c.value = -1
        assert c.value == TernaryValue.NEGATIVE
        assert c.formula is None

    def test_evaluate_runs_formula(self):
        c = Cell(formula=lambda: -1)
        result = c.evaluate()
        assert result == TernaryValue.NEGATIVE
        assert c.computed is True

    def test_reset_marks_stale(self):
        c = Cell(formula=lambda: 0)
        c.evaluate()
        assert c.computed is True
        c.reset()
        assert c.computed is False

    def test_static_cell_reset_is_noop(self):
        c = Cell(1)
        c.reset()
        assert c.computed is True  # no formula → always computed


# ── Grid tests ────────────────────────────────────────────────────────────

class TestGrid:
    def test_create_grid(self):
        g = Grid(3, 4)
        assert g.shape == (3, 4)

    def test_default_values(self):
        g = Grid(2, 2)
        for r in range(2):
            for c in range(2):
                assert g.get_value(r, c) == TernaryValue.ZERO

    def test_set_and_get(self):
        g = Grid(2, 2)
        g.set(0, 1, 1)
        assert g.get_value(0, 1) == TernaryValue.POSITIVE

    def test_getitem_syntax(self):
        g = Grid(2, 2)
        g[0, 0].value = -1
        assert g[0, 0].value == TernaryValue.NEGATIVE

    def test_out_of_bounds_raises(self):
        g = Grid(2, 2)
        with pytest.raises(IndexError):
            g.get(5, 0)

    def test_values_matrix(self):
        g = Grid(1, 3)
        g.set(0, 0, -1)
        g.set(0, 2, 1)
        vals = g.values()
        assert vals == [[-1, 0, 1]]

    def test_evaluate_runs_all_formulas(self):
        g = Grid(2, 1)
        g.set_formula(0, 0, lambda: 1)
        g.set_formula(1, 0, lambda: -1)
        g.evaluate()
        assert g.get_value(0, 0) == TernaryValue.POSITIVE
        assert g.get_value(1, 0) == TernaryValue.NEGATIVE

    def test_row_and_col(self):
        g = Grid(3, 2)
        g.set(1, 0, 1)
        g.set(1, 1, -1)
        row = g.row(1)
        assert [c.value for c in row] == [1, -1]
        col = g.col(0)
        assert [c.value for c in col] == [0, 1, 0]


# ── Formula tests ─────────────────────────────────────────────────────────

class TestFormulas:
    def test_sum_clamps_positive(self):
        g = Grid(4, 1)
        for r in range(3):
            g.set(r, 0, 1)
        g.set_formula(3, 0, SUM(lambda: g.get_value(0, 0),
                                lambda: g.get_value(1, 0),
                                lambda: g.get_value(2, 0)))
        assert g.evaluate().get_value(3, 0) == TernaryValue.POSITIVE

    def test_product_negative(self):
        g = Grid(2, 1)
        g.set(0, 0, 1)
        g.set(1, 0, -1)
        g2 = Grid(3, 1)
        g2.set(0, 0, 1)
        g2.set(1, 0, -1)
        g2.set_formula(2, 0, PRODUCT(lambda: g2.get_value(0, 0),
                                     lambda: g2.get_value(1, 0)))
        assert g2.evaluate().get_value(2, 0) == TernaryValue.NEGATIVE

    def test_threshold(self):
        g = Grid(4, 1)
        g.set(0, 0, 1)
        g.set(1, 0, 1)
        g.set(2, 0, 1)
        g.set_formula(3, 0, THRESHOLD(lambda: g.get_value(0, 0),
                                        lambda: g.get_value(1, 0),
                                        lambda: g.get_value(2, 0),
                                        threshold=2))
        assert g.evaluate().get_value(3, 0) == TernaryValue.POSITIVE

    def test_evolve_moves_toward_target(self):
        random.seed(42)
        g = Grid(2, 1)
        g.set(0, 0, -1)
        g.set_formula(1, 0, EVOLVE(lambda: g.get_value(0, 0), target=1, rate=1.0))
        g.evaluate()
        assert g.get_value(1, 0) in (TernaryValue.ZERO, TernaryValue.POSITIVE, TernaryValue.NEGATIVE)
        # With rate=1.0 and target=1, should move from -1 toward 0
        assert g.get_value(1, 0) == TernaryValue.ZERO

    def test_best_picks_max(self):
        g = Grid(3, 1)
        g.set(0, 0, -1)
        g.set(1, 0, 0)
        g.set(2, 0, 1)
        g2 = Grid(4, 1)
        g2.set(0, 0, -1)
        g2.set(1, 0, 0)
        g2.set(2, 0, 1)
        g2.set_formula(3, 0, BEST(lambda: g2.get_value(0, 0),
                                  lambda: g2.get_value(1, 0),
                                  lambda: g2.get_value(2, 0)))
        assert g2.evaluate().get_value(3, 0) == TernaryValue.POSITIVE


# ── Sort Engine tests ─────────────────────────────────────────────────────

class TestSortEngine:
    @staticmethod
    def _fitness(row):
        return sum(row)

    def test_scores(self):
        g = Grid(3, 2)
        g.set(0, 0, 1)
        g.set(0, 1, 1)   # fitness = 2
        g.set(1, 0, -1)
        g.set(1, 1, 0)   # fitness = -1
        g.set(2, 0, 0)
        g.set(2, 1, 1)   # fitness = 1
        se = SortEngine(g, self._fitness)
        scores = se.scores()
        assert scores == [2, -1, 1]

    def test_sort_descending(self):
        g = Grid(3, 1)
        g.set(0, 0, 0)
        g.set(1, 0, 1)
        g.set(2, 0, -1)
        se = SortEngine(g, self._fitness)
        order = se.sort_descending()
        assert order == [1, 0, 2]
        assert g.get_value(0, 0) == TernaryValue.POSITIVE

    def test_select_top(self):
        g = Grid(3, 1)
        g.set(0, 0, 1)
        g.set(1, 0, -1)
        g.set(2, 0, 0)
        se = SortEngine(g, self._fitness)
        top = se.select_top(1)
        assert top == [0]


# ── Autofill tests ────────────────────────────────────────────────────────

class TestAutofill:
    def test_autofill_copies_without_mutation(self):
        random.seed(0)
        g = Grid(3, 3)
        g.set(0, 0, 1)
        af = AutofillEngine(g, mutation_rate=0.0)
        af.autofill_row(0, 0, 2)
        assert g.get_value(0, 1) == TernaryValue.POSITIVE
        assert g.get_value(0, 2) == TernaryValue.POSITIVE

    def test_autofill_with_mutation(self):
        random.seed(99)
        g = Grid(5, 1)
        g.set(0, 0, 1)
        af = AutofillEngine(g, mutation_rate=1.0)
        af.autofill_col(0, 0, 4)
        # With mutation_rate=1.0, every cell should be random (not necessarily == 1)
        vals = [g.get_value(r, 0) for r in range(1, 5)]
        assert all(v in (-1, 0, 1) for v in vals)

    def test_autofill_rect(self):
        g = Grid(4, 4)
        g.set(0, 0, 1)
        g.set(0, 1, -1)
        g.set(1, 0, 0)
        g.set(1, 1, 1)
        af = AutofillEngine(g, mutation_rate=0.0)
        af.autofill(src=(0, 0, 1, 1), dst=(2, 0, 3, 3))
        # Tile: row 2 should be [1, -1, 1, -1]
        assert g.get_value(2, 0) == TernaryValue.POSITIVE
        assert g.get_value(2, 1) == TernaryValue.NEGATIVE
        assert g.get_value(2, 2) == TernaryValue.POSITIVE
        assert g.get_value(2, 3) == TernaryValue.NEGATIVE
