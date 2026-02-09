from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.proof.engine import derive
from sudologue.proof.proposition import RangeLemma
from sudologue.proof.rules.hidden_single import HiddenSingle


class TestHiddenSingle:
    def test_finds_hidden_single_in_row(self) -> None:
        # Row 3 has a hidden single for value 1 at (3,3)
        board = Board.from_string("1200001221000000", size=4)
        derivation = derive(board)
        theorems = HiddenSingle().apply(derivation)
        thm = next(t for t in theorems if t.cell == Cell(3, 3))
        assert thm.value == 1
        assert thm.rule == "hidden single"

    def test_premises_cover_house_domains(self) -> None:
        # Premises should include the range lemma for the house/value.
        board = Board.from_string("1200001221000000", size=4)
        derivation = derive(board)
        thm = next(t for t in HiddenSingle().apply(derivation) if t.cell == Cell(3, 3))
        assert len(thm.premises) == 1
        range_lemma = thm.premises[0]
        assert isinstance(range_lemma, RangeLemma)
        assert range_lemma.value == 1
        assert range_lemma.house.index == 3
        premise_cells = {elim.cell for elim in range_lemma.premises}
        assert premise_cells == {Cell(3, 0), Cell(3, 1), Cell(3, 2)}

    def test_no_hidden_single_on_empty_board(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        derivation = derive(board)
        assert HiddenSingle().apply(derivation) == []

    def test_no_duplicate_theorems_for_same_cell_value(self) -> None:
        """A hidden single in multiple houses should produce only one theorem."""
        board = Board.from_string("1200001221000000", size=4)
        derivation = derive(board)
        theorems = HiddenSingle().apply(derivation)
        keys = [(t.cell, t.value) for t in theorems]
        assert len(keys) == len(set(keys))
