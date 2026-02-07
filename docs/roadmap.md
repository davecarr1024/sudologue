# Roadmap

## Implementation Plan

Each step is built bottom-up: fully tested before the next layer starts. Every step gets its own commit.

### Step 1: Cell `model/cell.py`
- [x] Frozen dataclass `Cell(row, col)` with bounds validation
- [x] Tests for construction, validation, equality, hashing

### Step 2: House `model/house.py`
- [ ] `HouseType` enum (ROW, COLUMN, BOX)
- [ ] Frozen dataclass `House(house_type, index, cells)`
- [ ] Parameterized by board size: `houses_for_size(size)` generates all houses
- [ ] Lookup functions: `houses_for(cell, size)`, `peers(cell, size)`
- [ ] Tests for 4x4 house generation, peer lookups, box boundaries

### Step 3: Board `model/board.py`
- [ ] Frozen dataclass `Board(size, cells)` — placed values only, no candidates
- [ ] `__post_init__` validates all sudoku invariants
- [ ] `from_string(s, size)` factory, `value_at(cell)`, `place(cell, value)`
- [ ] `is_complete` property
- [ ] Tests focused on 4x4: construction, validation errors, placement, string parsing

### Step 4: Propositions `proof/proposition.py`
- [ ] `Axiom(cell, value)` — no premises
- [ ] `Elimination(cell, value, house, premises)` — tuple of Axiom premises
- [ ] `Lemma(cell, domain, premises)` — tuple of Elimination premises
- [ ] `Theorem(cell, value, rule, premises)` — tuple of Lemma premises
- [ ] `Proposition` union type alias
- [ ] Tests: construction, immutability, premise traversal, DAG sharing

### Step 5: Proof Engine `proof/engine.py`
- [ ] `Derivation` dataclass holding all axioms, eliminations, lemmas
- [ ] `derive(board) -> Derivation` — eagerly computes all propositions
- [ ] Tests: axiom extraction, elimination derivation, domain reduction, all on 4x4

### Step 6: Naked Single `proof/rules/naked_single.py`
- [ ] `Rule` protocol
- [ ] `NakedSingle.apply(derivation) -> Sequence[Theorem]`
- [ ] Tests: singleton domain produces theorem, multi-value domain does not

### Step 7: Solver `solver/`
- [ ] `SolveStatus` enum, `SolveResult` dataclass
- [ ] `Solver` with rule registration and solve loop
- [ ] Tests: single-step solve, multi-step solve, stuck detection

### Step 8: 4x4 End-to-End `puzzles/`
- [ ] Full 4x4 board solves with proof chain verification
- [ ] Multiple puzzles of varying difficulty

### Step 9: CLI
- [ ] `sudologue` command via poetry script entry point
- [ ] Load puzzle from string argument or file
- [ ] Print proof chain and solution
- [ ] `--size` flag for board size (default 9)

## Future Work

- Hidden single rule
- 9x9 puzzle solves
- Naked pair / hidden pair
- Pointing pairs / box-line reduction
- X-Wing, Swordfish
- Multiple narration styles
