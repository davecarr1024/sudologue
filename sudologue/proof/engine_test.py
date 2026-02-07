from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import HouseType
from sudologue.proof.engine import derive
from sudologue.proof.proposition import Axiom


class TestExtractAxioms:
    def test_empty_board(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        d = derive(board)
        assert len(d.axioms) == 0

    def test_three_givens(self) -> None:
        # 0001 / 0002 / 3000 / 0000
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        assert len(d.axioms) == 3
        assert Axiom(Cell(0, 3), 1) in d.axioms
        assert Axiom(Cell(1, 3), 2) in d.axioms
        assert Axiom(Cell(2, 0), 3) in d.axioms

    def test_scan_order(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        # Axioms should be in row-major scan order
        assert d.axioms[0] == Axiom(Cell(0, 3), 1)
        assert d.axioms[1] == Axiom(Cell(1, 3), 2)
        assert d.axioms[2] == Axiom(Cell(2, 0), 3)

    def test_full_board(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        d = derive(board)
        assert len(d.axioms) == 16


class TestDeriveEliminations:
    def test_empty_board_no_eliminations(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        d = derive(board)
        assert len(d.eliminations) == 0

    def test_single_given_eliminates_peers(self) -> None:
        # Only cell (0,0) = 1, rest empty
        board = Board.from_string("1000000000000000", size=4)
        d = derive(board)
        # Cell (0,0) has 7 peers, all empty. Each gets an elimination for 1.
        elim_cells = {e.cell for e in d.eliminations}
        assert Cell(0, 1) in elim_cells  # same row
        assert Cell(1, 0) in elim_cells  # same column
        assert Cell(1, 1) in elim_cells  # same box
        assert Cell(0, 0) not in elim_cells  # not self

    def test_no_duplicate_eliminations(self) -> None:
        # Cell (0,0) shares row AND box with (0,1) and (1,0) and (1,1).
        # Each (cell, value) pair should appear only once.
        board = Board.from_string("1000000000000000", size=4)
        d = derive(board)
        keys = [(e.cell, e.value) for e in d.eliminations]
        assert len(keys) == len(set(keys))

    def test_elimination_premises(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        # Find elimination: (2,3) ≠ 1
        elim = next(e for e in d.eliminations if e.cell == Cell(2, 3) and e.value == 1)
        assert len(elim.premises) == 1
        assert elim.premises[0] == Axiom(Cell(0, 3), 1)

    def test_elimination_house_type(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        # (2,3) ≠ 1 should cite column 3 (since (0,3) and (2,3) share col 3)
        elim = next(e for e in d.eliminations if e.cell == Cell(2, 3) and e.value == 1)
        assert elim.house.house_type == HouseType.COLUMN
        assert elim.house.index == 3

    def test_filled_peer_not_eliminated(self) -> None:
        # If a peer is already filled, no elimination is generated for it
        board = Board.from_string("1200000000000000", size=4)
        d = derive(board)
        # Cell (0,1)=2 is a peer of (0,0)=1, but (0,1) is filled
        elim_for_01 = [e for e in d.eliminations if e.cell == Cell(0, 1)]
        # Should NOT have an elimination for value 1 at (0,1)
        assert all(e.value != 1 for e in elim_for_01)

    def test_axiom_dag_sharing(self) -> None:
        """Multiple eliminations from the same axiom share the same object."""
        board = Board.from_string("1000000000000000", size=4)
        d = derive(board)
        axiom_ids = {id(e.premises[0]) for e in d.eliminations}
        # All eliminations cite the same axiom instance
        assert len(axiom_ids) == 1


class TestDeriveLemmas:
    def test_empty_board_full_domains(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        d = derive(board)
        assert len(d.lemmas) == 16
        for lemma in d.lemmas:
            assert lemma.domain == frozenset({1, 2, 3, 4})
            assert len(lemma.premises) == 0

    def test_singleton_domain(self) -> None:
        # From design doc: cell (2,3) should have domain {4}
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        lemma_23 = next(lem for lem in d.lemmas if lem.cell == Cell(2, 3))
        assert lemma_23.domain == frozenset({4})

    def test_domain_premises_are_eliminations(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        lemma_23 = next(lem for lem in d.lemmas if lem.cell == Cell(2, 3))
        # Should have 3 eliminations as premises: ≠1, ≠2, ≠3
        assert len(lemma_23.premises) == 3
        eliminated_values = {e.value for e in lemma_23.premises}
        assert eliminated_values == {1, 2, 3}

    def test_multi_value_domain(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        # Cell (3,3) is in col 3 (has 1, 2) and box 3 (no other givens there)
        # and row 3 (no givens). So eliminations: ≠1, ≠2. Domain = {3, 4}.
        lemma_33 = next(lem for lem in d.lemmas if lem.cell == Cell(3, 3))
        assert lemma_33.domain == frozenset({3, 4})

    def test_lemmas_in_scan_order(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        cells = [lem.cell for lem in d.lemmas]
        # Should be row-major, skipping filled cells
        assert cells[0] == Cell(0, 0)
        assert cells[1] == Cell(0, 1)
        assert cells[2] == Cell(0, 2)
        # (0,3) is filled, so next is (1,0)
        assert cells[3] == Cell(1, 0)

    def test_no_lemma_for_filled_cells(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)
        lemma_cells = {lem.cell for lem in d.lemmas}
        assert Cell(0, 3) not in lemma_cells
        assert Cell(1, 3) not in lemma_cells
        assert Cell(2, 0) not in lemma_cells


class TestDeriveRanges:
    def test_range_lemma_for_hidden_single(self) -> None:
        board = Board.from_string("1200001221000000", size=4)
        d = derive(board)
        range_lemma = next(
            rl
            for rl in d.range_lemmas
            if rl.house.house_type == HouseType.ROW
            and rl.house.index == 3
            and rl.value == 1
        )
        assert range_lemma.cells == (Cell(3, 3),)
        premise_cells = {elim.cell for elim in range_lemma.premises}
        assert premise_cells == {Cell(3, 0), Cell(3, 1), Cell(3, 2)}


class TestDerivationImmutability:
    def test_frozen(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        d = derive(board)
        import pytest

        with pytest.raises(AttributeError):
            d.axioms = ()  # type: ignore[misc]


class TestFullDerivation:
    """Integration test: derive everything and verify the design doc example."""

    def test_design_doc_example(self) -> None:
        board = Board.from_string("0001000230000000", size=4)
        d = derive(board)

        # 3 axioms
        assert len(d.axioms) == 3

        # Cell (2,3) has domain {4}
        lemma_23 = next(lem for lem in d.lemmas if lem.cell == Cell(2, 3))
        assert lemma_23.domain == frozenset({4})

        # The full proof chain is traceable
        for elim in lemma_23.premises:
            assert elim.cell == Cell(2, 3)
            assert len(elim.premises) == 1
            axiom = elim.premises[0]
            assert axiom.value == elim.value
