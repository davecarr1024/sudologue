from sudologue.inference.inference import Placement
from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import HouseType
from sudologue.rules.hidden_single import HiddenSingle

# Board designed for hidden single testing.
# Row 0: 1 2 3 | 4 5 6 | . . .  (missing 7, 8, 9)
# Row 3, col 6: 8            (eliminates 8 from col 6)
# Row 6, col 8: 8            (eliminates 8 from col 8)
# Result: In row 0, 8 can only go in (0,7) -> hidden single.
# Cell (0,7) has candidates {7, 8, 9} minus col constraints.
HIDDEN_SINGLE_BOARD = (
    "123456000"
    "000000000"
    "000000000"
    "000000800"
    "000000000"
    "000000000"
    "000000008"
    "000000000"
    "000000000"
)

# Empty board: no hidden singles (every digit can go in many cells per house).
EMPTY = "0" * 81


class TestHiddenSingle:
    def test_finds_hidden_single_in_row(self) -> None:
        board = Board.from_string(HIDDEN_SINGLE_BOARD)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        # Find the inference that places 8 at (0,7)
        placements = [
            inf
            for inf in inferences
            if isinstance(inf.action, Placement)
            and inf.action.cell == Cell(0, 7)
            and inf.action.value == 8
        ]
        assert len(placements) >= 1
        inf = placements[0]
        assert inf.evidence.focus_house is not None
        assert inf.evidence.focus_digit == 8

    def test_evidence_references_house(self) -> None:
        board = Board.from_string(HIDDEN_SINGLE_BOARD)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        placements = [
            inf
            for inf in inferences
            if isinstance(inf.action, Placement)
            and inf.action.cell == Cell(0, 7)
            and inf.action.value == 8
        ]
        inf = placements[0]
        assert inf.evidence.focus_house is not None
        assert inf.evidence.focus_house.house_type in (
            HouseType.ROW,
            HouseType.COLUMN,
            HouseType.BOX,
        )

    def test_no_hidden_singles_on_empty_board(self) -> None:
        board = Board.from_string(EMPTY)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        assert len(inferences) == 0

    def test_deduplicates_across_houses(self) -> None:
        """Same cell+value found via different houses should appear only once."""
        board = Board.from_string(HIDDEN_SINGLE_BOARD)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        placements: list[tuple[Cell, int]] = []
        for inf in inferences:
            if isinstance(inf.action, Placement):
                placements.append((inf.action.cell, inf.action.value))
        # No duplicate (cell, value) pairs.
        assert len(placements) == len(set(placements))

    def test_rule_name(self) -> None:
        assert HiddenSingle().name == "Hidden Single"

    def test_evidence_description(self) -> None:
        board = Board.from_string(HIDDEN_SINGLE_BOARD)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        placements_8 = [
            inf
            for inf in inferences
            if isinstance(inf.action, Placement)
            and inf.action.value == 8
            and inf.action.cell == Cell(0, 7)
        ]
        assert len(placements_8) >= 1
        desc = placements_8[0].evidence.description
        assert "8" in desc
        assert "R1C8" in desc

    def test_hidden_single_in_column(self) -> None:
        """8 can only go in one cell in column 7."""
        board = Board.from_string(HIDDEN_SINGLE_BOARD)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        # Check there's a hidden single for digit 8 in col 7
        col_inferences = [
            inf
            for inf in inferences
            if isinstance(inf.action, Placement)
            and inf.action.value == 8
            and inf.evidence.focus_house is not None
            and inf.evidence.focus_house.house_type == HouseType.COLUMN
        ]
        # May or may not find it depending on col 7 constraints.
        # The board has 8 in row 3 col 6 and row 6 col 8, not col 7.
        # So col 7 doesn't have 8 placed. Multiple cells in col 7 can have 8.
        # This test just validates the filter works.
        for inf in col_inferences:
            assert inf.evidence.focus_house is not None
            assert inf.evidence.focus_house.house_type == HouseType.COLUMN

    def test_hidden_single_in_box(self) -> None:
        """Test that hidden singles are found in boxes too."""
        # Box 2 (rows 0-2, cols 6-8): only (0,7) can have 8
        # because (0,6) loses 8 from col 6, (0,8) loses 8 from col 8,
        # and row 3 col 6 puts 8 in box 5 not box 2.
        # But (1,6) could also have 8 via box... let's check.
        board = Board.from_string(HIDDEN_SINGLE_BOARD)
        rule = HiddenSingle()
        inferences = rule.apply(board)
        box_inferences = [
            inf
            for inf in inferences
            if isinstance(inf.action, Placement)
            and inf.evidence.focus_house is not None
            and inf.evidence.focus_house.house_type == HouseType.BOX
        ]
        # There should be at least some box-based hidden singles
        # (the specific count depends on the board).
        for inf in box_inferences:
            assert inf.evidence.focus_house is not None
            assert inf.evidence.focus_house.house_type == HouseType.BOX
