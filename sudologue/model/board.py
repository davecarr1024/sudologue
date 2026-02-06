from dataclasses import dataclass
from typing import Final

from sudologue.model.cell import Cell
from sudologue.model.house import ALL_HOUSES, peers

DIGITS: Final[frozenset[int]] = frozenset(range(1, 10))


class BoardError(Exception):
    """Raised when a board state violates sudoku invariants."""


@dataclass(frozen=True, slots=True)
class Board:
    """Immutable sudoku board with placed values and per-cell candidates.

    Invariants enforced on construction:
    - Exactly 9x9 grid dimensions.
    - All values are None or digits 1-9.
    - No duplicate placed values within any house (row, column, box).
    - Placed cells have empty candidate sets.
    - Empty cells have non-empty candidate sets that are subsets of {1-9}.
    - Candidates do not include values already placed in peer cells.
    """

    cells: tuple[tuple[int | None, ...], ...]
    candidates: tuple[tuple[frozenset[int], ...], ...]

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if len(self.cells) != 9:
            raise BoardError(f"Expected 9 rows, got {len(self.cells)}")
        for r, row in enumerate(self.cells):
            if len(row) != 9:
                raise BoardError(f"Row {r}: expected 9 columns, got {len(row)}")
        if len(self.candidates) != 9:
            raise BoardError(f"Expected 9 candidate rows, got {len(self.candidates)}")
        for r, row in enumerate(self.candidates):
            if len(row) != 9:
                raise BoardError(
                    f"Candidate row {r}: expected 9 columns, got {len(row)}"
                )

        for r in range(9):
            for c in range(9):
                val = self.cells[r][c]
                cands = self.candidates[r][c]
                if val is not None:
                    if val not in DIGITS:
                        raise BoardError(f"Cell R{r + 1}C{c + 1}: invalid value {val}")
                    if cands:
                        raise BoardError(
                            f"Cell R{r + 1}C{c + 1}: placed cell must have "
                            f"empty candidates, got {cands}"
                        )
                else:
                    if not cands:
                        raise BoardError(
                            f"Cell R{r + 1}C{c + 1}: empty cell must have "
                            f"at least one candidate"
                        )
                    if not cands <= DIGITS:
                        raise BoardError(
                            f"Cell R{r + 1}C{c + 1}: candidates {cands} "
                            f"not a subset of {DIGITS}"
                        )

        # No duplicate placed values in any house.
        for house in ALL_HOUSES:
            seen: set[int] = set()
            for cell in house.cells:
                val = self.cells[cell.row][cell.col]
                if val is not None:
                    if val in seen:
                        raise BoardError(f"Duplicate value {val} in {house}")
                    seen.add(val)

        # Candidates must not include values placed in peer cells.
        for r in range(9):
            for c in range(9):
                if self.cells[r][c] is not None:
                    continue
                cell = Cell(r, c)
                cands = self.candidates[r][c]
                for peer in peers(cell):
                    peer_val = self.cells[peer.row][peer.col]
                    if peer_val is not None and peer_val in cands:
                        raise BoardError(
                            f"Cell {cell}: candidate {peer_val} conflicts "
                            f"with placed value in peer {peer}"
                        )

    @staticmethod
    def from_string(s: str) -> "Board":
        """Create a board from an 81-character string. '0' or '.' means empty."""
        if len(s) != 81:
            raise ValueError(f"Expected 81 characters, got {len(s)}")
        grid: list[list[int | None]] = []
        for row in range(9):
            grid_row: list[int | None] = []
            for col in range(9):
                ch = s[row * 9 + col]
                if ch in ("0", "."):
                    grid_row.append(None)
                elif ch.isdigit():
                    grid_row.append(int(ch))
                else:
                    raise ValueError(
                        f"Invalid character '{ch}' at position {row * 9 + col}"
                    )
            grid.append(grid_row)

        cells_tuple = tuple(tuple(row) for row in grid)

        cands: list[list[frozenset[int]]] = []
        for row in range(9):
            cand_row: list[frozenset[int]] = []
            for col in range(9):
                if grid[row][col] is not None:
                    cand_row.append(frozenset())
                else:
                    cell = Cell(row, col)
                    used: set[int] = set()
                    for p in peers(cell):
                        val = grid[p.row][p.col]
                        if val is not None:
                            used.add(val)
                    cand_row.append(DIGITS - used)
            cands.append(cand_row)

        return Board(cells=cells_tuple, candidates=tuple(tuple(row) for row in cands))

    def value_at(self, cell: Cell) -> int | None:
        """Return the placed value at the given cell, or None if empty."""
        return self.cells[cell.row][cell.col]

    def candidates_at(self, cell: Cell) -> frozenset[int]:
        """Return the candidate set for the given cell."""
        return self.candidates[cell.row][cell.col]

    @property
    def is_complete(self) -> bool:
        """True if every cell has a placed value."""
        return all(self.cells[r][c] is not None for r in range(9) for c in range(9))

    def place(self, cell: Cell, value: int) -> "Board":
        """Return a new board with value placed and candidates updated in peers."""
        new_cells = [list(row) for row in self.cells]
        new_cells[cell.row][cell.col] = value

        new_cands = [list(row) for row in self.candidates]
        new_cands[cell.row][cell.col] = frozenset()
        for peer in peers(cell):
            new_cands[peer.row][peer.col] = new_cands[peer.row][peer.col] - {value}

        return Board(
            cells=tuple(tuple(row) for row in new_cells),
            candidates=tuple(tuple(row) for row in new_cands),
        )

    def eliminate(self, cell: Cell, values: frozenset[int]) -> "Board":
        """Return a new board with candidate values removed from the given cell."""
        new_cands = [list(row) for row in self.candidates]
        new_cands[cell.row][cell.col] = new_cands[cell.row][cell.col] - values

        return Board(
            cells=self.cells,
            candidates=tuple(tuple(row) for row in new_cands),
        )

    def __str__(self) -> str:  # pragma: no cover
        lines: list[str] = []
        for r in range(9):
            if r in (3, 6):
                lines.append("------+-------+------")
            parts: list[str] = []
            for c in range(9):
                v = self.cells[r][c]
                parts.append(str(v) if v is not None else ".")
            line = (
                " ".join(parts[:3])
                + " | "
                + " ".join(parts[3:6])
                + " | "
                + " ".join(parts[6:])
            )
            lines.append(line)
        return "\n".join(lines)
