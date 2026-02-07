import math
from dataclasses import dataclass
from enum import Enum

from sudologue.model.cell import Cell


class HouseType(Enum):
    ROW = "row"
    COLUMN = "column"
    BOX = "box"


@dataclass(frozen=True)
class House:
    """A group of N cells that must contain digits 1-N exactly once."""

    house_type: HouseType
    index: int
    cells: tuple[Cell, ...]

    def __str__(self) -> str:
        return f"{self.house_type.value} {self.index}"


def _box_size(size: int) -> int:
    """Return the box dimension for a given board size (e.g., 2 for 4x4)."""
    bs = int(math.isqrt(size))
    if bs * bs != size:
        raise ValueError(f"Board size must be a perfect square, got {size}")
    return bs


def all_houses(size: int) -> tuple[House, ...]:
    """Generate all houses (rows, columns, boxes) for a board of given size."""
    bs = _box_size(size)
    houses: list[House] = []

    for r in range(size):
        houses.append(House(HouseType.ROW, r, tuple(Cell(r, c) for c in range(size))))

    for c in range(size):
        houses.append(
            House(HouseType.COLUMN, c, tuple(Cell(r, c) for r in range(size)))
        )

    for box_idx in range(size):
        box_row = (box_idx // bs) * bs
        box_col = (box_idx % bs) * bs
        cells = tuple(
            Cell(box_row + dr, box_col + dc) for dr in range(bs) for dc in range(bs)
        )
        houses.append(House(HouseType.BOX, box_idx, cells))

    return tuple(houses)


def houses_for(cell: Cell, size: int) -> tuple[House, ...]:
    """Return the houses containing the given cell."""
    return tuple(h for h in all_houses(size) if cell in h.cells)


def peers(cell: Cell, size: int) -> frozenset[Cell]:
    """Return all peer cells (cells sharing any house with the given cell)."""
    result: set[Cell] = set()
    for house in houses_for(cell, size):
        result.update(house.cells)
    result.discard(cell)
    return frozenset(result)
