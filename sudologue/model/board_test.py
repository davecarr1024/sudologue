import pytest

from sudologue.model.board import DIGITS, Board, BoardError
from sudologue.model.cell import Cell

PUZZLE = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)

SOLUTION = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)


class TestFromString:
    def test_valid_puzzle(self) -> None:
        board = Board.from_string(PUZZLE)
        assert board.value_at(Cell(0, 0)) == 5
        assert board.value_at(Cell(0, 1)) == 3
        assert board.value_at(Cell(0, 2)) is None

    def test_complete_solution(self) -> None:
        board = Board.from_string(SOLUTION)
        assert board.is_complete

    def test_invalid_length(self) -> None:
        with pytest.raises(ValueError, match="Expected 81 characters"):
            Board.from_string("123")

    def test_dots_as_empty(self) -> None:
        board = Board.from_string("." * 81)
        assert board.value_at(Cell(0, 0)) is None

    def test_invalid_character(self) -> None:
        with pytest.raises(ValueError, match="Invalid character"):
            Board.from_string("x" + "0" * 80)


class TestValueAt:
    def test_placed(self) -> None:
        board = Board.from_string(PUZZLE)
        assert board.value_at(Cell(0, 0)) == 5

    def test_empty(self) -> None:
        board = Board.from_string(PUZZLE)
        assert board.value_at(Cell(0, 2)) is None


class TestCandidatesAt:
    def test_placed_cell_has_no_candidates(self) -> None:
        board = Board.from_string(PUZZLE)
        assert board.candidates_at(Cell(0, 0)) == frozenset()

    def test_empty_cell_has_candidates(self) -> None:
        board = Board.from_string(PUZZLE)
        cands = board.candidates_at(Cell(0, 2))
        assert len(cands) > 0
        assert cands <= DIGITS

    def test_candidates_exclude_peer_values(self) -> None:
        board = Board.from_string(PUZZLE)
        # Row 0 has 5, 3, 7 placed. Candidates at (0, 2) should exclude those.
        cands = board.candidates_at(Cell(0, 2))
        assert 5 not in cands
        assert 3 not in cands
        assert 7 not in cands

    def test_candidates_exclude_column_values(self) -> None:
        board = Board.from_string(PUZZLE)
        # Column 0 has 5, 6, 8, 4, 7 placed.
        cands = board.candidates_at(Cell(2, 0))
        assert 5 not in cands
        assert 6 not in cands
        assert 8 not in cands
        assert 4 not in cands
        assert 7 not in cands

    def test_candidates_exclude_box_values(self) -> None:
        board = Board.from_string(PUZZLE)
        # Box 0 (rows 0-2, cols 0-2) has 5, 3, 6, 0, 9, 8.
        # Placed: 5, 3, 6, 9, 8
        cands = board.candidates_at(Cell(1, 1))
        assert 5 not in cands
        assert 3 not in cands
        assert 6 not in cands
        assert 9 not in cands
        assert 8 not in cands


class TestPlace:
    def test_updates_value(self) -> None:
        board = Board.from_string(PUZZLE)
        cell = Cell(0, 2)
        # The solution has 4 at (0, 2).
        new_board = board.place(cell, 4)
        assert new_board.value_at(cell) == 4

    def test_clears_candidates(self) -> None:
        board = Board.from_string(PUZZLE)
        cell = Cell(0, 2)
        new_board = board.place(cell, 4)
        assert new_board.candidates_at(cell) == frozenset()

    def test_removes_value_from_peer_candidates(self) -> None:
        board = Board.from_string(PUZZLE)
        cell = Cell(0, 2)
        # Find a peer that had 4 as a candidate before placement.
        peer = Cell(0, 3)
        had_four = 4 in board.candidates_at(peer)
        new_board = board.place(cell, 4)
        if had_four:
            assert 4 not in new_board.candidates_at(peer)

    def test_does_not_mutate_original(self) -> None:
        board = Board.from_string(PUZZLE)
        cell = Cell(0, 2)
        original_value = board.value_at(cell)
        _ = board.place(cell, 4)
        assert board.value_at(cell) == original_value


class TestEliminate:
    def test_removes_candidates(self) -> None:
        board = Board.from_string(PUZZLE)
        cell = Cell(0, 2)
        original = board.candidates_at(cell)
        assert len(original) > 1, "Need a cell with multiple candidates"
        to_keep = next(iter(original))
        to_remove = original - {to_keep}
        new_board = board.eliminate(cell, to_remove)
        assert new_board.candidates_at(cell) == {to_keep}

    def test_does_not_affect_other_cells(self) -> None:
        board = Board.from_string(PUZZLE)
        cell = Cell(0, 2)
        other = Cell(0, 3)
        original_other = board.candidates_at(other)
        to_remove = frozenset({next(iter(board.candidates_at(cell)))})
        new_board = board.eliminate(cell, to_remove)
        assert new_board.candidates_at(other) == original_other


class TestIsComplete:
    def test_incomplete(self) -> None:
        board = Board.from_string(PUZZLE)
        assert not board.is_complete

    def test_complete(self) -> None:
        board = Board.from_string(SOLUTION)
        assert board.is_complete


class TestInvariants:
    def test_duplicate_in_row(self) -> None:
        # Row 0: two 5s
        s = "550000000" + "0" * 72
        with pytest.raises(BoardError, match="Duplicate value 5"):
            Board.from_string(s)

    def test_duplicate_in_column(self) -> None:
        # Col 0: 5 at (0,0) and (1,0)
        s = "500000000" "500000000" + "0" * 63
        with pytest.raises(BoardError, match="Duplicate value 5"):
            Board.from_string(s)

    def test_duplicate_in_box(self) -> None:
        # Box 0: 5 at (0,0) and (1,1)
        s = "500000000" "050000000" + "0" * 63
        with pytest.raises(BoardError, match="Duplicate value 5"):
            Board.from_string(s)

    def test_placed_cell_with_candidates_rejected(self) -> None:
        """Directly constructing a board with a placed cell having candidates."""
        cells_list: list[list[int | None]] = [[None] * 9 for _ in range(9)]
        cands = tuple(
            tuple(frozenset(range(1, 10)) for _ in range(9)) for _ in range(9)
        )
        # Place value 5 at (0,0) but leave candidates non-empty.
        cells_list[0][0] = 5
        bad_cells = tuple(tuple(row) for row in cells_list)
        with pytest.raises(BoardError, match="placed cell must have empty candidates"):
            Board(cells=bad_cells, candidates=cands)

    def test_empty_cell_with_no_candidates_rejected(self) -> None:
        """An empty cell with no candidates is a contradiction."""
        cells = tuple(tuple(None for _ in range(9)) for _ in range(9))
        cands_list = [[frozenset(range(1, 10)) for _ in range(9)] for _ in range(9)]
        cands_list[0][0] = frozenset()
        bad_cands = tuple(tuple(row) for row in cands_list)
        with pytest.raises(BoardError, match="empty cell must have at least one"):
            Board(cells=cells, candidates=bad_cands)

    def test_candidate_conflicts_with_peer(self) -> None:
        """Candidate includes a value that's placed in a peer cell."""
        # Place 5 at (0,0). Cell (0,1) is a peer.
        # If (0,1) still has 5 as a candidate, that's invalid.
        cells_list: list[list[int | None]] = [[None] * 9 for _ in range(9)]
        cells_list[0][0] = 5
        cands_list = [[frozenset(range(1, 10)) for _ in range(9)] for _ in range(9)]
        cands_list[0][0] = frozenset()
        bad_cands = tuple(tuple(row) for row in cands_list)
        bad_cells = tuple(tuple(row) for row in cells_list)
        with pytest.raises(BoardError, match="candidate 5 conflicts"):
            Board(cells=bad_cells, candidates=bad_cands)


class TestStrFormatting:
    def test_has_separators(self) -> None:
        board = Board.from_string(PUZZLE)
        s = str(board)
        lines = s.split("\n")
        # 9 data rows + 2 separator rows = 11
        assert len(lines) == 11
        assert "------" in lines[3]
        assert "------" in lines[7]

    def test_has_pipes(self) -> None:
        board = Board.from_string(PUZZLE)
        s = str(board)
        for line in s.split("\n"):
            if "---" not in line:
                assert "|" in line
