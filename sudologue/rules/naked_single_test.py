from sudologue.inference.inference import Placement
from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.rules.naked_single import NakedSingle

# A nearly complete board: the known solution with one cell blanked out.
# Missing value 9 at position (8, 8).
ONE_MISSING = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286170"
)

# Same solution with two cells blanked: (8,7)=7 and (8,8)=9.
TWO_MISSING = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286100"
)

# Empty board: no naked singles possible (every cell has multiple candidates).
EMPTY = "0" * 81


class TestNakedSingle:
    def test_finds_single_naked_single(self) -> None:
        board = Board.from_string(ONE_MISSING)
        rule = NakedSingle()
        inferences = rule.apply(board)
        assert len(inferences) == 1
        inf = inferences[0]
        assert isinstance(inf.action, Placement)
        assert inf.action.cell == Cell(8, 8)
        assert inf.action.value == 9

    def test_finds_multiple_naked_singles(self) -> None:
        board = Board.from_string(TWO_MISSING)
        rule = NakedSingle()
        inferences = rule.apply(board)
        assert len(inferences) == 2
        cells_and_values: set[tuple[Cell, int]] = set()
        for inf in inferences:
            assert isinstance(inf.action, Placement)
            cells_and_values.add((inf.action.cell, inf.action.value))
        assert (Cell(8, 7), 7) in cells_and_values
        assert (Cell(8, 8), 9) in cells_and_values

    def test_no_naked_singles_on_empty_board(self) -> None:
        board = Board.from_string(EMPTY)
        rule = NakedSingle()
        inferences = rule.apply(board)
        assert len(inferences) == 0

    def test_no_naked_singles_on_complete_board(self) -> None:
        solution = (
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
        board = Board.from_string(solution)
        rule = NakedSingle()
        inferences = rule.apply(board)
        assert len(inferences) == 0

    def test_rule_name(self) -> None:
        assert NakedSingle().name == "Naked Single"

    def test_evidence_structure(self) -> None:
        board = Board.from_string(ONE_MISSING)
        rule = NakedSingle()
        inf = rule.apply(board)[0]
        assert inf.evidence.focus_cells == (Cell(8, 8),)
        assert inf.evidence.focus_house is None
        assert inf.evidence.focus_digit == 9
        assert inf.evidence.candidates_seen == frozenset({9})
        assert "R9C9" in inf.evidence.description
        assert "9" in inf.evidence.description
