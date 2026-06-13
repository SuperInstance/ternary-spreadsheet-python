# Ternary Spreadsheet (Python)

A **ternary spreadsheet** in Python — a grid of cells holding balanced ternary values (−1, 0, +1) with formula evaluation, sort engine, and mutation-based autofill. This package provides the same functionality as the C implementation with the ergonomics of Python: dataclasses, type hints, and `__init__.py` package structure.

## Why It Matters

Python is the lingua franca of data science and machine learning. A ternary spreadsheet in Python enables interactive exploration of ternary computation via Jupyter notebooks, integration with NumPy/Pandas for data pipelines, and use as a teaching tool for balanced ternary logic. The Python version emphasizes readability and composability over raw speed — making it ideal for prototyping ternary algorithms before implementing them in C or Rust. The sort engine and mutation-based autofill make ternary genetic algorithms accessible as spreadsheet operations, bridging the gap between visual spreadsheet thinking and programmatic optimization.

## How It Works

### Grid Model

The `Grid` class is an N×M matrix of `Cell` objects:

```python
class Grid:
    def __init__(self, rows: int, cols: int, default: TernaryValue = TernaryValue.NEUTRAL):
        self._cells = [[Cell(default) for _ in range(cols)] for _ in range(rows)]
```

Each `Cell` holds a `TernaryValue` (NEGATIVE, NEUTRAL, POSITIVE) and optional formula.

### TernaryValue Enum

```python
class TernaryValue(Enum):
    NEGATIVE = -1
    NEUTRAL  = 0
    POSITIVE = +1
```

Supports arithmetic: `POSITIVE + NEGATIVE → NEUTRAL` (truncated addition), `−POSITIVE → NEGATIVE` (negation).

### Formula Evaluation

Formulas are evaluated in dependency order:

```python
grid.set_formula(2, 2, Formula(type=FormulaType.SUM, r1=0, c1=0, r2=1, c2=1))
grid.evaluate()  # evaluates all formulas via topological sort
```

| Formula | Semantics | Example |
|---------|-----------|---------|
| SUM | Σ values clamped to [−1, +1] | SUM(A1:B2) = clamp(sum, −1, +1) |
| PRODUCT | Π values clamped | PRODUCT(A1:A3) = clamp(prod, −1, +1) |
| THRESHOLD | +1 if Σ > t, −1 if Σ < −t, else 0 | THRESHOLD(A1:A3, 1) |

### Sort Engine

Sorts a range by ternary fitness — rows with more positive values rank higher:

```python
sort_engine.sort(grid, r1=0, c1=0, r2=4, c2=4)
```

Fitness per row: `Σ (+1) − Σ (−1)`. O(N log N).

### Autofill

Mutated copy from a source range to a destination:

```python
autofill.fill(grid, src=(0,0,1,4), dst=(3,0,4,4), mutation_rate=10)
```

Each cell copies with `mutation_rate%` chance of a one-step ternary shift. This is a genetic operator — repeated autofill cycles evolve the grid's content.

## Quick Start

```bash
pip install -e src/
```

```python
from ternary_spreadsheet import Grid, TernaryValue

grid = Grid(5, 5)
grid.set(0, 0, TernaryValue.POSITIVE)
grid.set(0, 1, TernaryValue.NEGATIVE)

print(f"Cell(0,0) = {grid.get(0, 0)}")  # POSITIVE
print(f"Cell(0,1) = {grid.get(0, 1)}")  # NEGATIVE

# Evaluate formulas
grid.evaluate()

# Sort by fitness
from ternary_spreadsheet.sort_engine import sort_range
sort_range(grid, 0, 0, 4, 4)
```

## API

| Class/Module | Key Methods | Description |
|--------------|------------|-------------|
| `Grid` | `set`, `get`, `evaluate`, `set_formula` | Grid container and evaluator |
| `Cell` | `value`, `formula`, `has_formula` | Single ternary cell |
| `TernaryValue` | `NEGATIVE`, `NEUTRAL`, `POSITIVE` | Enum for ternary states |
| `Formula` | `type`, range coords, `threshold` | Formula definition |
| `sort_engine` | `sort_range(grid, ...)` | Fitness-based sort |
| `autofill` | `fill(grid, src, dst, rate)` | Mutation-based fill |

## Architecture Notes

The Python Ternary Spreadsheet mirrors the C version and serves as the high-level interface for ternary grid computation. In the γ + η = C framework, each cell is a ternary decision point: +1 (γ, constructive), −1 (η, avoidant), 0 (neutral). Formula evaluation propagates these values through dependency graphs, computing emergent competence C. The sort and autofill engines apply evolutionary dynamics — selection and mutation — making the spreadsheet a visual laboratory for γ/η dynamics. See [ARCHITECTURE.md](https://github.com/SuperInstance/SuperInstance/blob/main/ARCHITECTURE.md).

## References

1. Knuth, D. E. (1981). *TAOCP Vol. 2*. — Balanced ternary arithmetic.
2. Chambers, J. M. (2016). *Extending R*. CRC Press. — On extending data manipulation systems with new types.
3. McKinney, W. (2017). *Python for Data Analysis*, 2nd ed. O'Reilly. — Pandas DataFrame as a grid computation model.

## License

MIT
