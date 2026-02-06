# Sudologue

> A narration-first Sudoku solver: no guesses, only receipts.

Sudologue solves puzzles through pure logical deduction and explains its reasoning at every step. It never searches, never backtracks, and never guesses.

## Philosophy

Most sudoku solvers use backtracking search — they guess a value, see if it works, and backtrack if it doesn't. Sudologue takes the opposite approach: **every placement must be justified by a logical rule**. If the current set of rules can't make progress, the solver stops and says so rather than guessing.

The primary output of this project is a well-tested rule system, not a GUI. The test suite *is* the product — it demonstrates that each rule works correctly in isolation and that the rules combine to solve increasingly complex puzzles.

## Architecture

### Core Data Model

All core types are **frozen dataclasses** (immutable). Each solving step produces a new board state rather than mutating in place.

```
Cell(row: int, col: int)
    A position on the board. 0-indexed.

Board(cells: tuple[tuple[int | None, ...], ...],
      candidates: tuple[tuple[frozenset[int], ...], ...])
    The full board state. Each cell has either a placed value or a set
    of candidate values (possible digits). Placed cells have an empty
    candidate set. Candidates are derived from placed values on
    construction, then maintained incrementally as inferences are
    applied — each step narrows candidates rather than recomputing
    from scratch. Supports construction from an 81-character string
    and pretty-printing for display.

House
    A group of 9 cells that must contain digits 1-9 exactly once.
    Three types: Row, Column, Box. The board provides methods to
    retrieve houses and the peers of any cell.
```

### Inference System

An inference is a single deductive step: a rule observed something about the board and drew a conclusion. The conclusion is stored as **structured evidence** — machine-readable data about what the rule saw — not as a pre-baked string. Human-readable explanations are produced by narrators *from* the evidence, which means the same solve trace can be rendered in different voices.

```
Evidence(focus_cells: tuple[Cell, ...],
         focus_house: House | None,
         focus_digit: int | None,
         candidates_seen: frozenset[int] | None,
         description: str)
    Structured record of what the rule observed. The description is a
    terse, mechanical summary (for debugging); narrators produce the
    real prose.

Inference(rule: str,
          action: Placement | Elimination,
          evidence: Evidence)
    A single deductive step. Records which rule fired, what it
    concluded (place a value or eliminate candidates), and the
    structured evidence for why.

Placement(cell: Cell, value: int)
    Place a value in a cell.

Elimination(cells: tuple[Cell, ...],
            values: frozenset[int])
    Remove candidate values from one or more cells.

TraceStep(inference: Inference, board: Board)
    A paired snapshot: the inference that was applied and the
    resulting board state.

SolveResult(initial: Board,
            steps: tuple[TraceStep, ...],
            status: SolveStatus,
            diagnosis: str | None = None)
    The complete solve trace. Contains the starting board, every
    step, and whether the puzzle was solved or the solver got stuck
    (with a diagnosis of what's blocking progress).
```

### Rule System (Strategy Pattern)

Each rule implements a common `Rule` protocol:

```python
class Rule(Protocol):
    @property
    def name(self) -> str: ...

    def apply(self, board: Board) -> Sequence[Inference]: ...
```

A rule may return multiple possible inferences (e.g., Naked Single might see several cells that are each down to one candidate). The **solver picks one** per iteration — the first inference from the highest-priority rule that fires. This keeps the trace human-paced: one deduction, one new board, then re-evaluate.

Rules are registered with the `Solver` in priority order (simplest first). This ensures the simplest possible explanation is always preferred.

**Initial rules (in priority order):**

1. **Naked Single** — A cell has exactly one candidate remaining. It must be that value. *(Operates on per-cell candidates — the "domain" of a cell.)*

2. **Hidden Single** — A value has exactly one possible cell within a house (row, column, or box). It must go there. *(Operates on per-house value locations — the "range" of a value.)*

Further rules will be added incrementally as test puzzles demand them. Likely progression:

3. Naked Pair / Hidden Pair
4. Pointing Pairs / Box-Line Reduction
5. Naked Triple / Hidden Triple
6. X-Wing, Swordfish, and beyond

### Solver Loop

```
1. Initialize candidates for all empty cells from placed values.
2. Loop:
   a. Try each registered rule in priority order.
   b. Take the first inference from the first rule that fires.
   c. Apply it to produce a new board state. Record the TraceStep.
   d. If the board is complete, return SolveResult(status=SOLVED).
   e. If no rule fires, return SolveResult(status=STUCK) with a
      diagnosis describing the remaining candidates and why no rule
      could make progress.
3. The sequence of TraceSteps forms the solve trace.
```

### Narration

Inferences store structured evidence, not prose. **Narrators** render evidence into human-readable explanations. This separation means the same solve trace can be narrated in different voices — terse and technical, warm and conversational, or anywhere in between.

The narrator is not part of the core solver. It reads a `SolveResult` and produces text. This keeps the solver focused on deduction and the narrator focused on communication, and means narration can evolve independently of the rule system.

### Key Design Concepts

**Domain and Range.** When solving by hand, you track two things: which values can go in a cell (the *domain* — per-cell candidates) and where a value can go in a house (the *range* — per-value locations). The board state tracks domains explicitly. Ranges are derived by rules that need them (like Hidden Single). As the system evolves, these derivations may become composable inference steps themselves.

**Composability over complexity.** The design favors many simple, composable rules over fewer complex ones. A "smart" rule can be decomposed into a chain of simpler observations. This keeps each rule testable in isolation and makes the reasoning trace more transparent.

**One step at a time.** The solver applies exactly one inference per iteration, then re-evaluates. This produces a trace that reads like a human working through the puzzle — each step is a single thought, not a batch dump. It also means simpler rules get a chance to fire after each deduction, keeping explanations as simple as possible.

**Flat steps now, proof trees later.** Initially each inference operates independently on the current board state. As advanced rules require multi-step reasoning (e.g., "because of this naked pair, these candidates are eliminated, which reveals a hidden single"), the inference model can grow to reference prior inferences as premises, forming a proof tree.

## Project Structure

Tests live alongside the code they test. Full board solve tests live in a top-level `puzzles/` directory.

```
sudologue/
    __init__.py
    model/
        __init__.py
        cell.py              # Cell position
        cell_test.py
        board.py             # Board state with candidates
        board_test.py
        house.py             # Row, Column, Box definitions
        house_test.py
    inference/
        __init__.py
        inference.py         # Inference, Evidence, Placement, Elimination
        inference_test.py
        solve_result.py      # TraceStep, SolveResult, SolveStatus
        solve_result_test.py
    rules/
        __init__.py
        rule.py              # Rule protocol
        naked_single.py      # Naked Single rule
        naked_single_test.py
        hidden_single.py     # Hidden Single rule
        hidden_single_test.py
    solver/
        __init__.py
        solver.py            # Solver loop with rule registration
        solver_test.py
    narration/
        __init__.py
        narrator.py          # Narrator protocol and default narrator
        narrator_test.py
puzzles/
    __init__.py
    easy_test.py             # Full board solves: easy puzzles (singles only)
    medium_test.py           # Full board solves: medium puzzles
```

## Testing Strategy

**Rule isolation tests** — Each rule is tested with minimal board setups that exercise its logic:
- A board where the rule should fire and produce a specific inference
- A board where the rule should *not* fire (no deduction possible)
- Edge cases: multiple inferences in one pass, interactions with box/row/col boundaries

**Full board solve tests** — Complete puzzles as inline 81-character strings, verified to solve fully (or to a known stuck state when rules are insufficient):
```python
def test_easy_puzzle_001():
    board = Board.from_string(
        "530070000600195000098000060"
        "800060003400803001700020006"
        "060000280000419005000080079"
    )
    result = solver.solve(board)
    assert result.status == SolveStatus.SOLVED
    assert result.final_board.is_complete
```

**Puzzle progression** — As new rules are added, puzzles that previously returned `STUCK` should now solve. This forms a natural regression suite.

## Tooling

- **Python 3.14** — Latest language features
- **Poetry** — Dependency management
- **pyproject.toml** — Single-file project configuration
- **pytest** — Test framework with coverage via `pytest-cov`
- **pyright** (strict mode) — Static type checking (Pylance-compatible)
- **ruff** — Linting and import sorting
- **black** — Code formatting
- **poethepoet** — Task runner (`poe test`, `poe all`, etc.)

## Development Approach

The project is built iteratively:

1. **Core model** — `Cell`, `Board` (with 81-char string parsing and candidate initialization), `House` definitions. Full test coverage.

2. **Inference types** — `Evidence`, `Inference`, `Placement`, `Elimination`, `TraceStep`, `SolveResult`. Frozen dataclasses.

3. **Solver skeleton** — The main loop with rule registration, but no rules yet. Test that it returns `STUCK` on any non-trivial board.

4. **Naked Single** — First rule. Solve trivially-easy puzzles that only need naked singles.

5. **Hidden Single** — Second rule. Solve easy/medium puzzles. This is where the solver becomes practically useful.

6. **Expand** — Add rules one at a time, each motivated by a test puzzle that the current solver can't crack. Each new rule comes with its own isolation tests and at least one new full-board test.
