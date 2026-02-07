# Roadmap

## Implementation Plan

Each step is built bottom-up: fully tested before the next layer starts. Every step gets its own commit.

### Step 1: Cell `model/cell.py`
- [x] Frozen dataclass `Cell(row, col)` with bounds validation
- [x] Tests for construction, validation, equality, hashing

### Step 2: House `model/house.py`
- [x] `HouseType` enum (ROW, COLUMN, BOX)
- [x] Frozen dataclass `House(house_type, index, cells)`
- [x] Parameterized by board size: `all_houses(size)` generates all houses
- [x] Lookup functions: `houses_for(cell, size)`, `peers(cell, size)`
- [x] Tests for 4x4 house generation, peer lookups, box boundaries

### Step 3: Board `model/board.py`
- [x] Frozen dataclass `Board(size, cells)` — placed values only, no candidates
- [x] `__post_init__` validates all sudoku invariants
- [x] `from_string(s, size)` factory, `value_at(cell)`, `place(cell, value)`
- [x] `is_complete` property
- [x] Tests focused on 4x4: construction, validation errors, placement, string parsing

### Step 4: Propositions `proof/proposition.py`
- [x] `Axiom(cell, value)` — no premises
- [x] `Elimination(cell, value, house, premises)` — tuple of Axiom premises
- [x] `Lemma(cell, domain, premises)` — tuple of Elimination premises
- [x] `Theorem(cell, value, rule, premises)` — tuple of Lemma premises
- [x] `Proposition` union type alias
- [x] Tests: construction, immutability, premise traversal, DAG sharing

### Step 5: Proof Engine `proof/engine.py`
- [x] `Derivation` dataclass holding all axioms, eliminations, lemmas
- [x] `derive(board) -> Derivation` — eagerly computes all propositions
- [x] Tests: axiom extraction, elimination derivation, domain reduction, all on 4x4

### Step 6: Naked Single `proof/rules/naked_single.py`
- [x] `Rule` protocol
- [x] `NakedSingle.apply(derivation) -> Sequence[Theorem]`
- [x] Tests: singleton domain produces theorem, multi-value domain does not

### Step 7: Solver `solver/`
- [x] `SolveStatus` enum, `SolveResult` dataclass
- [x] `Solver` with rule registration and solve loop
- [x] Tests: single-step solve, multi-step solve, stuck detection

### Step 8: 4x4 End-to-End `puzzles/`
- [x] Full 4x4 board solves with proof chain verification
- [ ] Multiple puzzles of varying difficulty

### Step 9: CLI
- [x] `sudologue` command via poetry script entry point
- [x] Load puzzle from string argument or file
- [x] Print proof chain and solution
- [x] `--size` flag for board size (default 9)

## Future Work

- Hidden single rule
- 9x9 puzzle solves
- Naked pair / hidden pair
- Pointing pairs / box-line reduction
- X-Wing, Swordfish
- Multiple narration styles
