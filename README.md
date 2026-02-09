# Sudologue

> A Sudoku solver that never guesses — every placement is a proven theorem.

Sudologue solves puzzles through pure logical deduction. Every placement is backed by a formal proof — a chain of reasoning from axioms through lemmas to a theorem. It never searches, never backtracks, and never guesses.

## How It Works

Sudologue models sudoku reasoning using concepts from formal logic. Given a board, it:

1. Extracts **axioms** — the given values on the board.
2. Derives **eliminations** — "cell X can't be value V because it shares a house with a cell that already contains V."
3. Combines eliminations into **lemmas** — "cell X's remaining possible values are {4}."
4. Proves **theorems** — "cell X must be 4" — citing the lemmas as justification.

Each theorem is a proven placement backed by an inspectable proof chain. After placing a value, the solver re-derives everything from the new board and searches for the next theorem. This continues until the board is solved or no proof can be found.

### Example

Given a 4x4 board:

```
0 0 0 1
0 0 0 2
3 0 0 0
0 0 0 0
```

Sudologue proves cell (2,3) = 4:

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

## Usage

Solve a puzzle from a string (0 = empty):

```bash
sudologue "0001000230000000" --size 4
```

Solve from a file (one puzzle per line):

```bash
sudologue puzzles.txt
```

## Installation

Requires Python 3.13+.

```bash
poetry install
```

## Development

```bash
poe all       # format + lint + typecheck + test
poe test      # pytest only
poe typecheck # pyright strict
```

A pre-commit hook runs `poe all` before every commit.

## Documentation

- [Design](docs/design.md) — Architecture, data model, and proof system details
- [Roadmap](docs/roadmap.md) — Implementation plan and progress
