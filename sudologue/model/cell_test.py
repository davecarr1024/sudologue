import pytest

from sudologue.model.cell import Cell


class TestCellConstruction:
    def test_create_cell(self) -> None:
        cell = Cell(0, 0)
        assert cell.row == 0
        assert cell.col == 0

    def test_create_cell_nonzero(self) -> None:
        cell = Cell(3, 2)
        assert cell.row == 3
        assert cell.col == 2

    def test_negative_row_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            Cell(-1, 0)

    def test_negative_col_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            Cell(0, -1)


class TestCellEquality:
    def test_equal_cells(self) -> None:
        assert Cell(1, 2) == Cell(1, 2)

    def test_unequal_cells(self) -> None:
        assert Cell(1, 2) != Cell(2, 1)


class TestCellHashing:
    def test_same_cells_same_hash(self) -> None:
        assert hash(Cell(1, 2)) == hash(Cell(1, 2))

    def test_usable_in_set(self) -> None:
        cells = {Cell(0, 0), Cell(0, 0), Cell(1, 1)}
        assert len(cells) == 2

    def test_usable_as_dict_key(self) -> None:
        d: dict[Cell, int] = {Cell(0, 0): 1}
        assert d[Cell(0, 0)] == 1


class TestCellImmutability:
    def test_frozen(self) -> None:
        cell = Cell(0, 0)
        with pytest.raises(AttributeError):
            cell.row = 1  # type: ignore[misc]


class TestCellStr:
    def test_str(self) -> None:
        assert str(Cell(2, 3)) == "(2,3)"
