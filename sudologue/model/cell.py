from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    """A position on a sudoku board. 0-indexed."""

    row: int
    col: int

    def __post_init__(self) -> None:
        if self.row < 0 or self.col < 0:
            raise ValueError(
                f"row and col must be non-negative, got ({self.row}, {self.col})"
            )

    def __str__(self) -> str:
        return f"({self.row},{self.col})"
