# Ternary Spreadsheet

A spreadsheet engine where every cell is a tiny ternary agent with values **-1, 0, +1**.

## Installation

```bash
pip install ternary-spreadsheet
```

## Quick Start

```python
from ternary_spreadsheet import Grid, SUM, PRODUCT, THRESHOLD, EVOLVE, BEST

# Create a 4×3 grid (all zeros)
g = Grid(4, 3)

# Set some values
g.set(0, 0, 1)
g.set(1, 0, -1)

# Attach a formula: cell (2,0) = clamp(sum of row 0, col 0 + row 1, col 0)
g.set_formula(2, 0, SUM(lambda: g.get_value(0, 0),
                         lambda: g.get_value(1, 0)))
g.evaluate()
print(g.get_value(2, 0))  # → 0  (1 + -1 = 0)
```

## Concepts

### Ternary Values

Every cell holds one of three values: `+1`, `0`, or `-1`.

### Formulas

- **SUM** — sum references and clamp to ternary range
- **PRODUCT** — multiply references and clamp
- **THRESHOLD** — +1 if sum ≥ threshold, -1 if ≤ -threshold, else 0
- **EVOLVE** — probabilistically drift a value toward a target
- **BEST** — pick the maximum value from references

### Sort as Natural Selection

Rows are organisms; a fitness function scores them. The sort engine orders or selects rows by fitness.

```python
from ternary_spreadsheet import SortEngine

se = SortEngine(g, fitness=lambda row: sum(row))
se.sort_descending()  # fittest rows first
```

### Autofill as Mutation

Autofill copies source values into a target range with an optional mutation rate.

```python
from ternary_spreadsheet import AutofillEngine

af = AutofillEngine(g, mutation_rate=0.15)
af.autofill(src=(0, 0, 1, 1), dst=(2, 0, 3, 3))
```

## Development

```bash
PYTHONPATH=src pytest tests/ -v
```

## License

MIT
