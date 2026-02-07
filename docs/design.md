# Design

## Overview

Sudologue is a proof-first Sudoku solver. Every placement is a **theorem** supported by a **proof DAG** that traces back to the given board state. The solver never guesses; if no theorem can be proven, it stops.

## Core Propositions

Propositions are immutable facts with explicit premises. Together they form a proof DAG.

**Axiom** — A fact observed directly from the board.

```
Axiom: cell (0,3) = 1    [observed from board]
```

**Elimination (NotCandidate)** — A derived fact that a cell cannot contain a value, justified by premises. In early rules, eliminations are justified directly by axioms; future rules may justify eliminations via lemmas or ranges while preserving the same premise structure.

```
Elimination: (2,3) ≠ 1    [from: (0,3) = 1; shared house: column 3]
```

**Lemma (Domain)** — Remaining possible values for a cell, computed as base domain minus eliminations.

```
Lemma: domain of (2,3) = {4}    [from: (2,3) ≠ 1, (2,3) ≠ 2, (2,3) ≠ 3]
```

**RangeLemma (Range)** — Remaining possible cells for a value in a house after eliminations.

```
RangeLemma: range of row 3 for 1 = {(3,3)}    [from: (3,0) ≠ 1, (3,1) ≠ 1, (3,2) ≠ 1]
```

**Theorem** — A proven placement derived by a rule.

```
Theorem: place 4 at (2,3)    [from: domain of (2,3) = {4}; by naked single]
```

Every proposition is a frozen dataclass that holds its conclusion and premise references. Proofs are implicit in those references.

## Derived Views (Candidates, Domains, Ranges)

Candidates are a **derived view**: a value is a candidate if it has not been eliminated in the current derivation. Candidates are defined over the base domain `v ∈ {1..N}`. Eliminations remove values from this base domain for a specific cell.

```
Candidate(cell, v)  <=>  no elimination (cell ≠ v) exists in the derivation
```

From candidates we compute two projections:

```
Domain: domain(cell) = {v | Candidate(cell, v)}
Range:  range(house, v) = {cell in house | Candidate(cell, v)}
```

These views are computed, and Range is also materialized as a `RangeLemma` proposition for proof narration. This keeps proofs clean while allowing a future promotion to explicit `Candidate` nodes if needed.

**Derived-View Interfaces (stable API)**

1. `is_candidate(cell, value) -> bool`
2. `candidates(cell) -> frozenset[int]`
3. `domain(cell) -> frozenset[int]` (alias of `candidates(cell)`)
4. `range(house, value) -> tuple[Cell, ...]`
5. `candidates_in_house(house) -> dict[Cell, frozenset[int]]`

## Proof DAG

Proofs are DAGs, not trees. Shared subproofs are never duplicated.

```mermaid
flowchart TD
  A[Axiom] --> E[Elimination]
  E --> L[Domain Lemma]
  L --> T[Theorem]
```

Each theorem is immutable and tied to the board state at the step it was proven. After a placement, the solver re-derives all propositions from the new board.

## Inference Rules

**Built-in derivations** (computed every step):

1. **Axiom extraction** — create axioms for all placed values.
2. **Elimination** — for each axiom, eliminate that value from peer cells.
3. **Domain reduction** — for each empty cell, compute its domain lemma.
4. **Range reduction** — for each `(house, value)`, compute its range lemma.

**Theorem-producing rules** (priority order):

1. **Naked single** — if `domain(cell)` has size 1, place it.
2. **Hidden single** — for each `(house, value)`, compute `range(house, value)`; if it has size 1, place it. Premises should be **targeted eliminations** proving `¬Candidate` for every other cell in the house. `Candidate(target, value)` is implied (can be included in full/strict proofs later).

Further rules are added incrementally as tests demand them.

## Proof Shapes (Rule-Level)

**Naked single (domain-first)**

```
Theorem(place v at cell)
  <- Lemma(domain(cell) = {v})
      <- Eliminations(cell ≠ v_i) for the values ruled out in this step (base domain minus these eliminations yields {v})
          <- Axioms that justify those eliminations
```

```mermaid
flowchart TD
  A1[Axioms] --> E1[Eliminations for cell]
  E1 --> L1[Domain Lemma]
  L1 --> T1[Theorem: place v at cell]
```

**Hidden single (range-first, minimal premises)**

```
Theorem(place v at target)  [hidden single in house H]
  <- RangeLemma(range(H, v) = {target})
     <- Eliminations(other_cell ≠ v) for all other cells in H
        <- Axioms (via house relationships)
```

```mermaid
flowchart TD
  A2[Axioms] --> E2[Eliminations: other cells ≠ v]
  E2 --> R2[Range Lemma]
  R2 --> T2[Theorem: place v at target]
```

## Narration Policy

Narration is a policy layer, not rule logic:

1. **Naked single narration** — domain-first: “domain(cell) = {v}”.
2. **Hidden single narration** — range-first by default: “in this house, value v can only go in cell X”.

Styles may override these defaults without changing correctness.

## Solver Loop

```mermaid
flowchart TD
  S[Start board] --> D[Derive axioms, eliminations, domains]
  D --> R[Apply rules in priority order]
  R -->|Theorem found| P[Place value and record step]
  P --> D
  R -->|No theorem| X[Stuck]
```

The solver applies exactly one theorem per iteration, producing a human-paced trace.

## Architecture

All core types are frozen dataclasses. Each step produces a new board rather than mutating in place.

```
Cell(row, col)
House(type, index, cells)
Board(size, cells)
```

Boards validate invariants on construction: no duplicate values in any house and all values within 1..N.

## Future Extensions (Range-First + Minimization)

1. **Candidate promotion** — if needed for narration or advanced rules, introduce a computed or explicit `Candidate` node without breaking the interface layer.
2. **Proof minimization** — keep derivation maximal; slice explanations lazily at narration time. Minimization is backward slicing of the proof DAG from a theorem, optionally dropping redundant premises per narration policy. Optional eager scoring can be used to choose among competing theorems.
3. **Advanced rules** — naked/hidden pairs, pointing pairs, box-line reduction, X-Wing, Swordfish.
4. **Stable proposition IDs** — propositions can be hashable by `(type, conclusion fields)` to enable de-duplication and proof slicing without relying on instance identity.

## Testing Strategy

Tests use **4x4 boards** for clarity and brevity, scaling to 9x9 for full puzzles.

**Proposition tests** — Verify individual inference rules in isolation:
- Given a board, assert the correct axioms are extracted
- Given axioms, assert the correct eliminations are derived
- Given eliminations, assert the correct domain lemmas are produced
- Given a singleton domain, assert the correct theorem is proven

**Proof tests** — Verify complete derivations for a single placement:
- Given a board, assert the solver proves a specific placement
- Assert the proof chain contains the expected premises

**Full board solve tests** — Complete puzzles verified to solve fully:
```python
def test_4x4_solve():
    board = Board.from_string("0001000230000000", size=4)
    result = solver.solve(board)
    assert result.status == SolveStatus.SOLVED
```

**Progression tests** — As new inference rules are added, puzzles that previously returned `STUCK` should now solve.

## Project Structure

Tests live alongside the code they test. Full board solve tests live in a top-level `puzzles/` directory.

```
sudologue/
    model/
        cell.py              # Cell position
        house.py             # Row, Column, Box; peer/house lookups
        board.py             # Board state, parameterized by size
    proof/
        proposition.py       # Axiom, Elimination, Lemma, Theorem
        engine.py            # Derives propositions from board state
        rules/
            naked_single.py  # Domain = {v} -> place v
            hidden_single.py # Value in only one cell in house -> place
    solver/
        solver.py            # Solve loop: derive -> prove -> place -> repeat
        solve_result.py      # SolveResult, SolveStatus
    narration/
        narrator.py          # Proof chain -> human-readable text
puzzles/
    four_by_four_test.py     # 4x4 full board solves
    nine_by_nine_test.py     # 9x9 solve using singles
```

## Tooling

- **Python 3.12+** — Modern language features without pinning to pre-release runtimes
- **Poetry** — Dependency management
- **pyproject.toml** — Single-file project configuration
- **pytest** — Test framework with coverage via `pytest-cov`
- **pyright** (strict mode) — Static type checking (Pylance-compatible)
- **ruff** — Linting and import sorting
- **black** — Code formatting
- **poethepoet** — Task runner (`poe test`, `poe all`, etc.)
