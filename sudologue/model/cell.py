from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cell:
    """A position on the sudoku board. 0-indexed."""

    row: int
    col: int

    def __post_init__(self) -> None:
        if not (0 <= self.row < 9):
            raise ValueError(f"row must be 0-8, got {self.row}")
        if not (0 <= self.col < 9):
            raise ValueError(f"col must be 0-8, got {self.col}")

    def __str__(self) -> str:
        return f"R{self.row + 1}C{self.col + 1}"
