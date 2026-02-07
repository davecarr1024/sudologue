import pytest

from sudologue.model.board import Board
from sudologue.model.cell import Cell


class TestFromString4x4:
    def test_empty_board(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        assert board.size == 4
        assert board.value_at(Cell(0, 0)) is None

    def test_with_givens(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        assert board.value_at(Cell(0, 3)) == 1
        assert board.value_at(Cell(1, 3)) == 2
        assert board.value_at(Cell(2, 0)) == 3
        assert board.value_at(Cell(0, 0)) is None

    def test_full_board(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        assert board.value_at(Cell(0, 0)) == 1
        assert board.value_at(Cell(3, 3)) == 1

    def test_wrong_length(self) -> None:
        with pytest.raises(ValueError, match="Expected 16 characters"):
            Board.from_string("000", size=4)

    def test_invalid_character(self) -> None:
        with pytest.raises(ValueError, match="Invalid character"):
            Board.from_string("000x000000000000", size=4)


class TestFromString9x9:
    def test_empty(self) -> None:
        board = Board.from_string("0" * 81, size=9)
        assert board.size == 9

    def test_wrong_length(self) -> None:
        with pytest.raises(ValueError, match="Expected 81 characters"):
            Board.from_string("0" * 80, size=9)


class TestValidation:
    def test_wrong_row_count(self) -> None:
        with pytest.raises(ValueError, match="Expected 4 rows"):
            Board(size=4, cells=((None,) * 4,) * 3)

    def test_wrong_col_count(self) -> None:
        with pytest.raises(ValueError, match="expected 4 cols"):
            Board(
                size=4,
                cells=(
                    (None, None, None),
                    (None,) * 4,
                    (None,) * 4,
                    (None,) * 4,
                ),
            )

    def test_value_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="out of range"):
            Board.from_string("5000000000000000", size=4)

    def test_value_zero_is_none(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        assert board.value_at(Cell(0, 0)) is None

    def test_duplicate_in_row(self) -> None:
        with pytest.raises(ValueError, match="Duplicate"):
            Board.from_string("1100000000000000", size=4)

    def test_duplicate_in_column(self) -> None:
        with pytest.raises(ValueError, match="Duplicate"):
            Board.from_string("1000100000000000", size=4)

    def test_duplicate_in_box(self) -> None:
        with pytest.raises(ValueError, match="Duplicate"):
            Board.from_string("1000010000000000", size=4)


class TestPlace:
    def test_place_returns_new_board(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        new_board = board.place(Cell(0, 0), 1)
        assert new_board.value_at(Cell(0, 0)) == 1
        assert board.value_at(Cell(0, 0)) is None  # original unchanged

    def test_place_on_filled_cell_raises(self) -> None:
        board = Board.from_string("1000000000000000", size=4)
        with pytest.raises(ValueError, match="already filled"):
            board.place(Cell(0, 0), 2)

    def test_place_validates_invariants(self) -> None:
        board = Board.from_string("1000000000000000", size=4)
        with pytest.raises(ValueError, match="Duplicate"):
            board.place(Cell(0, 1), 1)  # same row

    def test_sequential_placements(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        board = board.place(Cell(0, 0), 1)
        board = board.place(Cell(0, 1), 2)
        assert board.value_at(Cell(0, 0)) == 1
        assert board.value_at(Cell(0, 1)) == 2


class TestIsComplete:
    def test_empty_is_not_complete(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        assert not board.is_complete

    def test_partial_is_not_complete(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        assert not board.is_complete

    def test_full_is_complete(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        assert board.is_complete


class TestEmptyCells:
    def test_all_empty(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        assert len(board.empty_cells) == 16

    def test_some_filled(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        empty = board.empty_cells
        assert len(empty) == 13
        assert Cell(0, 3) not in empty
        assert Cell(1, 3) not in empty
        assert Cell(2, 0) not in empty

    def test_full_board_no_empty(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        assert len(board.empty_cells) == 0

    def test_scan_order(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        empty = board.empty_cells
        # Should be row-major order
        assert empty[0] == Cell(0, 0)
        assert empty[1] == Cell(0, 1)
        assert empty[2] == Cell(0, 2)
        # Cell(0,3) is filled, so next is Cell(1,0)
        assert empty[3] == Cell(1, 0)


class TestImmutability:
    def test_frozen(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        with pytest.raises(AttributeError):
            board.size = 9  # type: ignore[misc]
