# CLAUDE.md

## Project Overview

Sudologue is a proof-based Sudoku solver written in pure Python 3.13+. Every cell placement is a formally proven theorem backed by an auditable proof chain — no guessing or backtracking. The solver treats Sudoku as a formal logic problem where propositions form a DAG from axioms (given values) through eliminations and lemmas to theorems (placements).

## Quick Reference

```bash
poetry install                  # Install dependencies
poetry run poe all              # Format + lint + typecheck + test (the full CI check)
poetry run poe test             # Run tests only
poetry run poe typecheck        # Pyright strict mode
poetry run poe format           # Black formatting
poetry run poe lint             # Ruff linting with auto-fix
```

## Architecture

```
sudologue/
├── model/           # Domain model: Cell, Board, House
├── proof/           # Proof system: propositions, derivation engine
│   └── rules/       # Inference rules (naked single, hidden single)
├── solver/          # Solve loop: derive → apply rules → place → repeat
├── narration/       # Output verbosity policies
└── cli.py           # Command-line entry point
puzzles/             # Integration tests (4x4 and 9x9 full-board solves)
docs/                # design.md (formal spec) and roadmap.md
```

### Layer Responsibilities

- **model/** — Immutable board state, cell positions, house definitions (rows, columns, boxes). `Board.place()` returns a new board; nothing mutates.
- **proof/** — The core reasoning engine. `engine.derive(board)` eagerly computes all propositions (axioms, eliminations, lemmas, range lemmas, candidates) in a single pass to saturation.
- **proof/rules/** — Inference rules implement `SelectionRule` or `EliminationRule` protocols. Rules consume a `Derivation` and produce theorems or eliminations.
- **solver/** — Orchestrates the loop: derive all propositions, apply rules in priority order, pick one theorem, place it, repeat until solved or stuck.
- **narration/** — Verbosity enum (`TERSE`, `NORMAL`, `FULL`) for controlling proof output depth.

### Proposition Types (proof DAG nodes)

`Axiom` → `Elimination` → `Lemma` / `RangeLemma` → `Candidate` → `Theorem`

- **Axiom** — Given value observed from the board
- **Elimination** — Cell cannot contain a value (the only atomic effect)
- **Lemma** — Domain (remaining candidates) for a cell
- **RangeLemma** — Cells in a house where a value can go (first-class, used by all rules)
- **Candidate** — Possible value for a cell (derived from domain)
- **Theorem** — Proven placement with rule name and premises

## Code Conventions

### Immutability Everywhere

All domain types are `@dataclass(frozen=True)`. Boards, propositions, and proof chains are immutable. Each solver step creates a new `Board` via `board.place(cell, value)`.

### Type Safety

Pyright runs in **strict mode** on `sudologue/`. All functions and attributes must have type annotations. Use `X | Y` union syntax, `Sequence`, `tuple`, `frozenset`, `dict` generics. Rule interfaces use `Protocol` (structural typing), not inheritance.

### Test Conventions

- Tests are **colocated** with source: `module_test.py` next to `module.py`
- Pytest pattern: `*_test.py` (not `test_*.py`)
- Full-board integration tests live in `puzzles/`
- Use `unittest`-style classes (`TestClassName`) with `test_method_name` methods
- 4x4 boards for unit test clarity; 9x9 for integration puzzles
- `pytest-subtests` for parameterized test cases

### Naming

- Classes: `PascalCase` — `Board`, `Cell`, `Axiom`, `RangeLemma`
- Functions/methods: `snake_case` — `derive_eliminations`, `format_board`
- Private: `_leading_underscore`
- Type aliases: `PascalCase` — `Proposition`, `Premise`, `HouseLike`
- Constants: `UPPER_CASE`

### No Runtime Dependencies

The solver is pure Python with zero runtime dependencies. All packages in `pyproject.toml` are dev/test tools only.

## Development Workflow

### Running the Full Check Suite

```bash
poetry run poe all    # Runs: format → lint → typecheck → test
```

This is the same check the pre-commit hook and CI pipeline run. Always pass this before committing.

### Individual Commands

| Command | Tool | What It Does |
|---------|------|-------------|
| `poetry run poe format` | Black | Auto-format code (line-length 88) |
| `poetry run poe lint` | Ruff | Lint + auto-fix (E, F, I, B rules) |
| `poetry run poe typecheck` | Pyright | Strict type checking |
| `poetry run poe test` | Pytest | Run all tests with coverage |

### Pre-Commit Hook

`.githooks/pre-commit` runs `poe all` before every commit and auto-stages formatting changes. Configure with:

```bash
git config core.hooksPath .githooks
```

### CI Pipeline

GitHub Actions (`.github/workflows/ci.yml`) runs on pushes to `main` and all PRs:
1. Format check (`black --check`)
2. Lint (`ruff check`)
3. Type check (`pyright`)
4. Test (`pytest`)

All four must pass.

## Key Design Decisions

1. **Range-first reasoning** — `RangeLemma` is the first-class proposition consumed by all rules. Domain lemmas exist for narration but rules depend on ranges.
2. **Single theorem per iteration** — The solver places exactly one value per loop cycle for human-readable traces.
3. **Priority-ordered rules** — Rules are tried in order (naked single before hidden single). The first rule that fires wins. An optional scorer picks among multiple theorems from the same rule.
4. **Proposition identity** — `prop_id()` generates stable hashable IDs from `(type, conclusion_fields)` for deduplication across derivations.
5. **Proof minimization** — `slice_proof()` performs backward DAG traversal to extract minimal proof chains at different verbosity levels.
6. **Elimination is the only atomic effect** — All other propositions are derived views. Eliminations justify everything upstream.

## Roadmap Context

Phases 1-3 are complete (proof identity, range lemmas, proof minimization). Phase 4 (pointing pairs / box-line reduction) is partially done. Phases 5-6 (structure lemmas, advanced fish patterns like X-Wing/Swordfish) are planned. See `docs/roadmap.md` for details.

## Common Tasks for AI Assistants

### Adding a New Inference Rule

1. Create `sudologue/proof/rules/your_rule.py` implementing `SelectionRule` or `EliminationRule` protocol
2. Create `sudologue/proof/rules/your_rule_test.py` with colocated tests
3. If it's an elimination rule, integrate into the saturation loop in `engine.py`
4. If it's a selection rule, add it to the solver's rule list (in priority order)
5. Add puzzle test cases in `puzzles/` that require the new rule
6. Run `poetry run poe all` to verify

### Adding a New Proposition Type

1. Define as a frozen dataclass in `sudologue/proof/proposition.py`
2. Add to the `Proposition` union type alias
3. Implement `prop_id()` support in `identity.py`
4. Update `engine.py` derivation to produce the new proposition
5. Update `minimizer.py` if it needs special slicing behavior
6. Update `cli.py` formatting if it should appear in output

### Debugging a Stuck Puzzle

The solver returns `SolveStatus.STUCK` when no rule can fire. To debug:
1. Call `derive(board)` on the stuck board state
2. Inspect `derivation.range_lemmas` and `derivation.domain_lemmas`
3. Check if any range has size 1 (hidden single) or any domain has size 1 (naked single)
4. If candidates exist but no rule fires, a new rule is needed
