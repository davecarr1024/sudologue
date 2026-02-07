from dataclasses import dataclass

from sudologue.model.cell import Cell
from sudologue.model.house import all_houses


@dataclass(frozen=True)
class Board:
    """Immutable sudoku board state. Stores only placed values."""

    size: int
    cells: tuple[tuple[int | None, ...], ...]

    def __post_init__(self) -> None:
        if len(self.cells) != self.size:
            raise ValueError(f"Expected {self.size} rows, got {len(self.cells)}")
        for r, row in enumerate(self.cells):
            if len(row) != self.size:
                raise ValueError(f"Row {r}: expected {self.size} cols, got {len(row)}")
            for c, val in enumerate(row):
                if val is not None and (val < 1 or val > self.size):
                    raise ValueError(
                        f"Cell ({r},{c}): value {val} out of range " f"1-{self.size}"
                    )

        for house in all_houses(self.size):
            placed: list[int] = []
            for cell in house.cells:
                v = self.cells[cell.row][cell.col]
                if v is not None:
                    placed.append(v)
            if len(placed) != len(set(placed)):
                raise ValueError(f"Duplicate value in {house}")

    @classmethod
    def from_string(cls, s: str, size: int = 9) -> "Board":
        """Parse a compact string where '0' means empty."""
        if len(s) != size * size:
            raise ValueError(f"Expected {size * size} characters, got {len(s)}")
        rows: list[tuple[int | None, ...]] = []
        for r in range(size):
            row: list[int | None] = []
            for c in range(size):
                ch = s[r * size + c]
                if not ch.isdigit():
                    raise ValueError(
                        f"Invalid character '{ch}' at position " f"{r * size + c}"
                    )
                val = int(ch)
                row.append(None if val == 0 else val)
            rows.append(tuple(row))
        return cls(size=size, cells=tuple(rows))

    def value_at(self, cell: Cell) -> int | None:
        """Return the placed value at a cell, or None if empty."""
        return self.cells[cell.row][cell.col]

    def place(self, cell: Cell, value: int) -> "Board":
        """Return a new board with the given value placed at the cell."""
        if self.cells[cell.row][cell.col] is not None:
            raise ValueError(f"Cell {cell} is already filled")
        rows = list(self.cells)
        row = list(rows[cell.row])
        row[cell.col] = value
        rows[cell.row] = tuple(row)
        return Board(size=self.size, cells=tuple(rows))

    @property
    def is_complete(self) -> bool:
        """True if all cells are filled."""
        return all(
            self.cells[r][c] is not None
            for r in range(self.size)
            for c in range(self.size)
        )

    @property
    def empty_cells(self) -> tuple[Cell, ...]:
        """Return all empty cells in row-major scan order."""
        result: list[Cell] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.cells[r][c] is None:
                    result.append(Cell(r, c))
        return tuple(result)
