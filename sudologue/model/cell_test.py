import pytest

from sudologue.model.cell import Cell


class TestCell:
    def test_creation(self) -> None:
        cell = Cell(0, 0)
        assert cell.row == 0
        assert cell.col == 0

    def test_creation_max(self) -> None:
        cell = Cell(8, 8)
        assert cell.row == 8
        assert cell.col == 8

    def test_invalid_row_negative(self) -> None:
        with pytest.raises(ValueError, match="row must be 0-8"):
            Cell(-1, 0)

    def test_invalid_row_too_large(self) -> None:
        with pytest.raises(ValueError, match="row must be 0-8"):
            Cell(9, 0)

    def test_invalid_col_negative(self) -> None:
        with pytest.raises(ValueError, match="col must be 0-8"):
            Cell(0, -1)

    def test_invalid_col_too_large(self) -> None:
        with pytest.raises(ValueError, match="col must be 0-8"):
            Cell(0, 9)

    def test_equality(self) -> None:
        assert Cell(3, 4) == Cell(3, 4)
        assert Cell(3, 4) != Cell(4, 3)

    def test_hash(self) -> None:
        cells = {Cell(0, 0), Cell(0, 0), Cell(1, 1)}
        assert len(cells) == 2

    def test_str(self) -> None:
        assert str(Cell(0, 0)) == "R1C1"
        assert str(Cell(8, 8)) == "R9C9"
        assert str(Cell(2, 4)) == "R3C5"

    def test_frozen(self) -> None:
        cell = Cell(0, 0)
        with pytest.raises(AttributeError):
            cell.row = 1  # type: ignore[misc]
