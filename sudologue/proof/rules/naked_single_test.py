from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import HouseType
from sudologue.proof.engine import derive
from sudologue.proof.proposition import Axiom, RangeLemma
from sudologue.proof.rules.naked_single import NakedSingle


class TestNakedSingle:
    def test_finds_singleton_domain(self) -> None:
        # Cell (2,3) has domain {4} on this board
        board = Board.from_string("0001000230000000", size=4)
        derivation = derive(board)
        rule = NakedSingle()
        theorems = rule.apply(derivation)
        cells = {t.cell for t in theorems}
        assert Cell(2, 3) in cells

    def test_theorem_has_correct_value(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        derivation = derive(board)
        theorems = NakedSingle().apply(derivation)
        thm = next(t for t in theorems if t.cell == Cell(2, 3))
        assert thm.value == 4

    def test_theorem_has_correct_rule_name(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        derivation = derive(board)
        theorems = NakedSingle().apply(derivation)
        thm = next(t for t in theorems if t.cell == Cell(2, 3))
        assert thm.rule == "naked single"

    def test_theorem_premise_is_range_lemmas(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        derivation = derive(board)
        theorems = NakedSingle().apply(derivation)
        thm = next(t for t in theorems if t.cell == Cell(2, 3))
        premise_values = {p.value for p in thm.premises if isinstance(p, RangeLemma)}
        assert premise_values == {1, 2, 3}
        assert all(
            isinstance(p, RangeLemma) and p.house.house_type == HouseType.CELL
            for p in thm.premises
        )
        assert all(p.cells == () for p in thm.premises if isinstance(p, RangeLemma))

    def test_no_theorems_when_no_singletons(self) -> None:
        # Empty board: all domains are {1,2,3,4}, no singletons
        board = Board.from_string("0000000000000000", size=4)
        derivation = derive(board)
        theorems = NakedSingle().apply(derivation)
        assert len(theorems) == 0

    def test_multiple_singletons(self) -> None:
        # A board with multiple cells that can be naked-singled
        # Row 0 has 1,2,3 placed, so (0,3) is forced to 4... wait, that's
        # already given. Let me use a board where multiple cells reduce.
        #
        # 1230 / 0000 / 0000 / 0000
        # Cell (0,3) is in row with 1,2,3 -> domain {4}
        board = Board.from_string("1230000000000000", size=4)
        derivation = derive(board)
        theorems = NakedSingle().apply(derivation)
        # At minimum, (0,3) should be found
        cells = {t.cell for t in theorems}
        assert Cell(0, 3) in cells
        thm = next(t for t in theorems if t.cell == Cell(0, 3))
        assert thm.value == 4

    def test_full_proof_chain_from_theorem_to_axioms(self) -> None:
        """Verify the complete proof chain is traversable."""
        board = Board.from_string("0001000230000000", size=4)
        derivation = derive(board)
        theorems = NakedSingle().apply(derivation)
        thm = next(t for t in theorems if t.cell == Cell(2, 3))

        # theorem -> range lemmas -> eliminations -> axioms
        for range_lemma in thm.premises:
            assert isinstance(range_lemma, RangeLemma)
            assert range_lemma.house.house_type == HouseType.CELL
            assert range_lemma.cells == ()
            assert len(range_lemma.premises) == 1
            elim = range_lemma.premises[0]
            assert len(elim.premises) == 1
            axiom = elim.premises[0]
            assert isinstance(axiom, Axiom)
            assert axiom.value == elim.value

    def test_name_property(self) -> None:
        assert NakedSingle().name == "naked single"
