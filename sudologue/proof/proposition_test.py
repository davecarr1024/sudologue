import pytest

from sudologue.model.cell import Cell
from sudologue.model.house import House, HouseType, all_houses
from sudologue.proof.proposition import (
    Axiom,
    Candidate,
    Elimination,
    Lemma,
    NotCandidate,
    RangeLemma,
    Theorem,
)


def _row0_4x4() -> House:
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.ROW and h.index == 0
    )


def _col3_4x4() -> House:
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.COLUMN and h.index == 3
    )


class TestAxiom:
    def test_construction(self) -> None:
        ax = Axiom(Cell(0, 3), 1)
        assert ax.cell == Cell(0, 3)
        assert ax.value == 1

    def test_str(self) -> None:
        assert str(Axiom(Cell(0, 3), 1)) == "(0,3) = 1"

    def test_frozen(self) -> None:
        ax = Axiom(Cell(0, 0), 1)
        with pytest.raises(AttributeError):
            ax.value = 2  # type: ignore[misc]

    def test_equality(self) -> None:
        assert Axiom(Cell(0, 3), 1) == Axiom(Cell(0, 3), 1)
        assert Axiom(Cell(0, 3), 1) != Axiom(Cell(0, 3), 2)


class TestElimination:
    def test_construction(self) -> None:
        ax = Axiom(Cell(0, 3), 1)
        col = _col3_4x4()
        elim = Elimination(Cell(2, 3), 1, col, (ax,))
        assert elim.cell == Cell(2, 3)
        assert elim.value == 1
        assert elim.house == col
        assert elim.premises == (ax,)

    def test_str(self) -> None:
        ax = Axiom(Cell(0, 3), 1)
        elim = Elimination(Cell(2, 3), 1, _col3_4x4(), (ax,))
        assert str(elim) == "(2,3) ≠ 1"

    def test_premises_are_tuple(self) -> None:
        ax = Axiom(Cell(0, 3), 1)
        elim = Elimination(Cell(2, 3), 1, _col3_4x4(), (ax,))
        assert isinstance(elim.premises, tuple)

    def test_frozen(self) -> None:
        ax = Axiom(Cell(0, 3), 1)
        elim = Elimination(Cell(2, 3), 1, _col3_4x4(), (ax,))
        with pytest.raises(AttributeError):
            elim.value = 2  # type: ignore[misc]

    def test_non_axiom_premise(self) -> None:
        lemma = Lemma(Cell(0, 1), frozenset({3, 4}), ())
        elim = Elimination(Cell(0, 2), 3, _row0_4x4(), (lemma,))
        assert elim.premises == (lemma,)


class TestNotCandidate:
    def test_alias(self) -> None:
        ax = Axiom(Cell(0, 3), 1)
        nc = NotCandidate(Cell(2, 3), 1, _col3_4x4(), (ax,))
        assert isinstance(nc, Elimination)
        assert str(nc) == "(2,3) ≠ 1"


class TestLemma:
    def test_construction(self) -> None:
        ax1 = Axiom(Cell(0, 3), 1)
        ax2 = Axiom(Cell(1, 3), 2)
        ax3 = Axiom(Cell(2, 0), 3)
        col = _col3_4x4()
        row = _row0_4x4()
        e1 = Elimination(Cell(2, 3), 1, col, (ax1,))
        e2 = Elimination(Cell(2, 3), 2, col, (ax2,))
        e3 = Elimination(Cell(2, 3), 3, row, (ax3,))
        lemma = Lemma(Cell(2, 3), frozenset({4}), (e1, e2, e3))
        assert lemma.cell == Cell(2, 3)
        assert lemma.domain == frozenset({4})
        assert len(lemma.premises) == 3

    def test_str(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        assert str(lemma) == "domain of (2,3) = {4}"

    def test_str_multiple_values(self) -> None:
        lemma = Lemma(Cell(1, 1), frozenset({2, 4}), ())
        assert str(lemma) == "domain of (1,1) = {2, 4}"

    def test_frozen(self) -> None:
        lemma = Lemma(Cell(0, 0), frozenset({1, 2}), ())
        with pytest.raises(AttributeError):
            lemma.domain = frozenset({1})  # type: ignore[misc]


class TestRangeLemma:
    def test_construction(self) -> None:
        house = _row0_4x4()
        rl = RangeLemma(house, 2, (Cell(0, 1), Cell(0, 2)), ())
        assert rl.house == house
        assert rl.value == 2
        assert rl.cells == (Cell(0, 1), Cell(0, 2))

    def test_str(self) -> None:
        house = _row0_4x4()
        rl = RangeLemma(house, 2, (Cell(0, 1),), ())
        assert str(rl) == f"range of {house} for 2 = {{(0,1)}}"

    def test_frozen(self) -> None:
        house = _row0_4x4()
        rl = RangeLemma(house, 2, (Cell(0, 1),), ())
        with pytest.raises(AttributeError):
            rl.value = 3  # type: ignore[misc]


class TestCandidate:
    def test_construction(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        cand = Candidate(Cell(2, 3), 4, (lemma,))
        assert cand.cell == Cell(2, 3)
        assert cand.value == 4
        assert cand.premises == (lemma,)

    def test_str(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        cand = Candidate(Cell(2, 3), 4, (lemma,))
        assert str(cand) == "candidate (2,3) = 4"

    def test_frozen(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        cand = Candidate(Cell(2, 3), 4, (lemma,))
        with pytest.raises(AttributeError):
            cand.value = 1  # type: ignore[misc]


class TestTheorem:
    def test_construction(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        thm = Theorem(Cell(2, 3), 4, "naked single", (lemma,))
        assert thm.cell == Cell(2, 3)
        assert thm.value == 4
        assert thm.rule == "naked single"
        assert thm.premises == (lemma,)

    def test_str(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        thm = Theorem(Cell(2, 3), 4, "naked single", (lemma,))
        assert str(thm) == "place 4 at (2,3)"

    def test_frozen(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        thm = Theorem(Cell(2, 3), 4, "naked single", (lemma,))
        with pytest.raises(AttributeError):
            thm.value = 1  # type: ignore[misc]


class TestProofChain:
    """Test that proof chains can be traversed from theorem to axioms."""

    def test_full_chain(self) -> None:
        # Build the example proof from the design doc
        ax1 = Axiom(Cell(0, 3), 1)
        ax2 = Axiom(Cell(1, 3), 2)
        ax3 = Axiom(Cell(2, 0), 3)

        col3 = _col3_4x4()
        row2 = next(
            h for h in all_houses(4) if h.house_type == HouseType.ROW and h.index == 2
        )

        e1 = Elimination(Cell(2, 3), 1, col3, (ax1,))
        e2 = Elimination(Cell(2, 3), 2, col3, (ax2,))
        e3 = Elimination(Cell(2, 3), 3, row2, (ax3,))

        lemma = Lemma(Cell(2, 3), frozenset({4}), (e1, e2, e3))
        theorem = Theorem(Cell(2, 3), 4, "naked single", (lemma,))

        # Traverse: theorem -> lemma -> eliminations -> axioms
        assert theorem.premises[0] is lemma
        assert lemma.premises[0] is e1
        assert lemma.premises[1] is e2
        assert lemma.premises[2] is e3
        assert e1.premises[0] is ax1
        assert e2.premises[0] is ax2
        assert e3.premises[0] is ax3

    def test_dag_sharing(self) -> None:
        """Multiple eliminations can share the same axiom object."""
        ax = Axiom(Cell(0, 0), 1)
        row = _row0_4x4()
        e1 = Elimination(Cell(0, 1), 1, row, (ax,))
        e2 = Elimination(Cell(0, 2), 1, row, (ax,))
        # Both eliminations reference the same axiom instance
        assert e1.premises[0] is e2.premises[0]
