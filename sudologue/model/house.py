from dataclasses import dataclass
from enum import Enum
from typing import Final

from sudologue.model.cell import Cell


class HouseType(Enum):
    ROW = "row"
    COLUMN = "column"
    BOX = "box"


@dataclass(frozen=True, slots=True)
class House:
    """A group of 9 cells that must contain digits 1-9 exactly once."""

    house_type: HouseType
    index: int
    cells: tuple[Cell, ...]

    def __str__(self) -> str:
        return f"{self.house_type.value} {self.index + 1}"


def _build_all_houses() -> tuple[House, ...]:
    houses: list[House] = []
    for i in range(9):
        houses.append(House(HouseType.ROW, i, tuple(Cell(i, c) for c in range(9))))
        houses.append(House(HouseType.COLUMN, i, tuple(Cell(r, i) for r in range(9))))
    for br in range(3):
        for bc in range(3):
            cells = tuple(
                Cell(br * 3 + r, bc * 3 + c) for r in range(3) for c in range(3)
            )
            houses.append(House(HouseType.BOX, br * 3 + bc, cells))
    return tuple(houses)


ALL_HOUSES: Final[tuple[House, ...]] = _build_all_houses()


def _build_houses_by_cell() -> dict[Cell, tuple[House, ...]]:
    result: dict[Cell, tuple[House, ...]] = {}
    for r in range(9):
        for c in range(9):
            cell = Cell(r, c)
            result[cell] = tuple(h for h in ALL_HOUSES if cell in h.cells)
    return result


_HOUSES_BY_CELL: Final[dict[Cell, tuple[House, ...]]] = _build_houses_by_cell()


def _build_peers_by_cell() -> dict[Cell, frozenset[Cell]]:
    result: dict[Cell, frozenset[Cell]] = {}
    for r in range(9):
        for c in range(9):
            cell = Cell(r, c)
            peer_set: set[Cell] = set()
            for house in _HOUSES_BY_CELL[cell]:
                peer_set.update(house.cells)
            peer_set.discard(cell)
            result[cell] = frozenset(peer_set)
    return result


_PEERS_BY_CELL: Final[dict[Cell, frozenset[Cell]]] = _build_peers_by_cell()


def houses_for(cell: Cell) -> tuple[House, ...]:
    """Return the three houses (row, column, box) containing the given cell."""
    return _HOUSES_BY_CELL[cell]


def peers(cell: Cell) -> frozenset[Cell]:
    """Return all cells that share a house with the given cell (excluding itself)."""
    return _PEERS_BY_CELL[cell]
