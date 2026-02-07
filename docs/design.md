# Design

## The Proof System

Sudologue models sudoku reasoning using concepts from formal logic. Each solving step produces a **theorem** (a proven placement) supported by a **proof** — a chain of propositions where every step cites the premises it was derived from.

### Propositions

A **proposition** is a statement about the board that has been proven true. Propositions form a hierarchy, from directly observed facts up through derived conclusions:

**Axiom** — A fact observed directly from the board. Axioms have no premises; they are self-evident.

```
Axiom: cell (0,3) = 1    [observed from board]
```

**Elimination** — A derived proposition that a cell cannot contain a certain value. Each elimination cites its premises: an axiom (the placed value) and the house relationship that connects the two cells.

```
Elimination: (2,3) ≠ 1    [from: (0,3) = 1; shared house: column 3]
```

**Lemma** — An intermediate conclusion derived by combining other propositions. For example, **domain reduction** collects all eliminations for a cell to determine its remaining possible values.

```
Lemma: domain of (2,3) = {4}    [from: (2,3) ≠ 1, (2,3) ≠ 2, (2,3) ≠ 3]
```

**Range Lemma** — A complementary statement that, for a given house and value, lists the only cells where that value can appear. It is the dual of a domain lemma: instead of proving what a cell can contain, it proves where a value must live within a house.

```
Range Lemma: in Box 3, value 1 ∈ {(2,3), (3,3)}
```

Range lemmas compose naturally with eliminations: if all candidate cells for a value in a box lie in a single row or column, that value can be eliminated from the rest of that row or column outside the box (pointing pairs/box-line reduction).

**Theorem** — A proven placement. The final conclusion of a proof chain. A theorem cites the lemma (or lemmas) that justify it, and through them, the full chain back to axioms.

```
Theorem: place 4 at (2,3)    [from: domain of (2,3) = {4}; by naked single]
```

Every proposition is a frozen dataclass that holds its conclusion and a reference to its premises. You can trace any theorem back through lemmas, eliminations, and axioms to the raw board state.

### Proofs

A **proof** is the complete chain of propositions leading to a theorem. It is not a separate data structure — it is implicit in the premise references. Walking a theorem's premises recursively yields the full proof DAG.

Propositions are shared, not copied. When multiple eliminations reference the same axiom, they hold references to the same `Axiom` object. This makes proofs a DAG (directed acyclic graph), not a tree — shared subproofs are never duplicated.

Each theorem is an **immutable artifact** of the solver step that produced it. The proof chain captures the reasoning that was valid at that step's board state. After a placement is applied, the next step re-derives fresh propositions from the new board — the old theorem and its proof chain are frozen in the solve trace, never modified.

### Inference Rules

An **inference rule** is a mechanism that derives new propositions from existing ones. Each rule takes the current board state (and/or existing propositions) as input and produces new propositions with their premises linked.

**Built-in derivations** (applied automatically every step):

1. **Axiom extraction** — Scan the board and produce an axiom for each placed value.
2. **Elimination** — For each axiom, produce an elimination for every empty peer cell: "value V is at cell A, and cell B shares a house with A, therefore B ≠ V."
3. **Domain reduction** — For each empty cell, collect all its eliminations and compute the remaining possible values as a lemma.

**Theorem-producing rules** (applied in priority order, first by rule order, then by cell scan order for deterministic traces):

1. **Naked single** — If a cell's domain has exactly one value, that value must be placed there. The theorem's premise is the single domain lemma.

2. **Hidden single** — Within a house, if a value appears in only one cell's domain, it must go there. The theorem's premises are the domain lemmas for every cell in the house — together they prove that the value has exactly one possible location.

Further inference rules will be added incrementally as test puzzles demand them. Likely progression:

3. Naked pair / hidden pair
4. Pointing pairs / box-line reduction
5. Naked triple / hidden triple
6. X-Wing, Swordfish, and beyond

Each new rule produces theorems from increasingly sophisticated combinations of lemmas — but every proof still traces back to axioms and eliminations at the leaves.

### Example Proof

Given a 4x4 board:

```
0 0 0 1
0 0 0 2
3 0 0 0
0 0 0 0
```

Proof that cell (2,3) = 4:

```
1. Axiom:       (0,3) = 1                       [observed]
2. Axiom:       (1,3) = 2                       [observed]
3. Axiom:       (2,0) = 3                       [observed]
4. Elimination: (2,3) ≠ 1                       [from 1; same column]
5. Elimination: (2,3) ≠ 2                       [from 2; same column]
6. Elimination: (2,3) ≠ 3                       [from 3; same row]
7. Lemma:       domain of (2,3) = {4}           [from 4, 5, 6]
8. Theorem:     place 4 at (2,3)                [from 7; naked single]
```

Each step references its premises. The proof is machine-generated but human-readable.

## Architecture

### Board Model

All core types are **frozen dataclasses** (immutable). Each solving step produces a new board state rather than mutating in place.

```
Cell(row, col)
    A position on the board. 0-indexed.

House
    A group of N cells that must contain digits 1-N exactly once.
    Three types: Row, Column, Box.

Board(size, cells)
    The full board state. Parameterized by size (4 for 4x4, 9 for 9x9).
    Validates all sudoku invariants on construction: no duplicate values
    in any house, all values in range 1-N. Empty cells are represented
    as None internally; in the compact string format, '0' denotes empty
    (e.g., "0001000230000000" for a 4x4 board with three givens).
```

The board validates invariants in `__post_init__`, so an invalid board state cannot exist. After every placement, the new board is constructed and validated.

### Proposition Types

All propositions are frozen dataclasses. Premises are stored as tuples (immutable sequences) so that proof objects are fully immutable end-to-end.

```
Axiom(cell, value)
    A given value observed on the board. No premises.

Elimination(cell, value, house, premises: tuple[Axiom, ...])
    Cell cannot contain value because of a placed value in a shared house.
    - house: the House (row, column, or box) that connects the two cells.
    - premises: the axiom(s) that justify the elimination.

Lemma(cell, domain, premises: tuple[Elimination, ...])
    The remaining possible values for a cell after all eliminations.
    The base domain is {1..N} for an NxN board (e.g., {1,2,3,4} for 4x4).
    Each elimination removes one value; the lemma records what remains.
    - premises: the eliminations that narrowed the domain.

Theorem(cell, value, rule, premises: tuple[Lemma, ...])
    A proven placement.
    - rule: the name of the inference rule that justified the placement
      (e.g., "naked single", "hidden single").
    - premises: the lemma(s) that the rule operated on.
```

### Solver

The solver is a simple loop:

```
1. Derive all axioms, eliminations, and lemmas from the board state.
2. Apply inference rules to search for a theorem.
3. If a theorem is found:
   a. Apply the placement to produce a new board.
   b. Validate the new board's invariants.
   c. Record the step (theorem + new board state).
   d. Repeat from 1.
4. If no theorem can be proven: stop and report what's blocking progress.
```

Each iteration produces exactly one placement, keeping the trace human-paced: one proof, one new board, then re-derive and search again.

### Narration

Because every theorem carries its full proof chain, narration is just proof rendering. Walk the premise references and describe each step. Different renderers can produce different styles — terse, conversational, formal — all from the same proof structure.

## Key Design Principles

**Proofs, not procedures.** A procedural solver embeds its reasoning in rule code — you see the answer but not the argument. In this design, the reasoning *is* the output — a composable proof chain where each step cites its premises.

**Composability.** Complex reasoning emerges from combining simple propositions. A naked single proof is: axioms -> eliminations -> domain lemma -> theorem. A hidden single proof combines domain lemmas across a house. Future rules (naked pairs, X-Wings) compose the same building blocks in new ways.

Range lemmas add a second, dual building block: domain lemmas are cell-centric; range lemmas are value-in-house-centric. Together they support more complex reasoning (pointing pairs, box-line reduction, and other candidate eliminations) while preserving the same atomic proof chain.

## Complex Constructions (Atomic + Composable)

More advanced logic still follows the same atomic style: build small propositions, then compose them into a theorem.

**Hidden single proof shape.** A hidden single uses only existing lemmas. The rule gathers the domain lemmas for a house and proves that a value occurs in exactly one domain. The theorem cites all house lemmas as premises, preserving a full proof chain without introducing new proposition types.

**Set-based reasoning (future).** Patterns like naked/hidden pairs, pointing pairs, and X-Wing will introduce *candidate eliminations* that are not directly tied to a single axiom. These will be represented as first-class propositions whose premises are domain lemmas (and, transitively, eliminations and axioms). This keeps the logic atomic: each elimination is still a discrete proposition, but its justification is a composable chain of smaller propositions rather than a monolithic rule.

**Independence.** Each reasoning step takes the board as its sole input and produces a new board plus a proof. There is no mutable state carried between steps. After every placement, the solver starts fresh — re-deriving axioms, eliminations, and lemmas from the new board.

**One step at a time.** The solver applies exactly one theorem per iteration, then re-evaluates. This produces a trace that reads like a human working through the puzzle — each step is a single thought, not a batch dump.

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
    easy_test.py             # 9x9 easy puzzles
    medium_test.py           # 9x9 medium puzzles
```

## Tooling

- **Python 3.14** — Latest language features
- **Poetry** — Dependency management
- **pyproject.toml** — Single-file project configuration
- **pytest** — Test framework with coverage via `pytest-cov`
- **pyright** (strict mode) — Static type checking (Pylance-compatible)
- **ruff** — Linting and import sorting
- **black** — Code formatting
- **poethepoet** — Task runner (`poe test`, `poe all`, etc.)
