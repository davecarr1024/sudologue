from sudologue.model.cell import Cell
from sudologue.model.house import HouseType, all_houses
from sudologue.narration.policy import Verbosity
from sudologue.proof.minimizer import slice_proof
from sudologue.proof.proposition import Axiom, Elimination, Lemma, Theorem


def _row2_4x4():
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.ROW and h.index == 2
    )


def _col3_4x4():
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.COLUMN and h.index == 3
    )


def _build_theorem() -> Theorem:
    ax1 = Axiom(Cell(0, 3), 1)
    ax2 = Axiom(Cell(1, 3), 2)
    ax3 = Axiom(Cell(2, 0), 3)

    e1 = Elimination(Cell(2, 3), 1, _col3_4x4(), (ax1,))
    e2 = Elimination(Cell(2, 3), 2, _col3_4x4(), (ax2,))
    e3 = Elimination(Cell(2, 3), 3, _row2_4x4(), (ax3,))

    lemma = Lemma(Cell(2, 3), frozenset({4}), (e1, e2, e3))
    return Theorem(Cell(2, 3), 4, "naked single", (lemma,))


class TestSliceProof:
    def test_full_slice_includes_axioms(self) -> None:
        thm = _build_theorem()
        result = slice_proof(thm, Verbosity.FULL)
        assert any(isinstance(prop, Axiom) for prop in result)

    def test_normal_slice_excludes_axioms(self) -> None:
        thm = _build_theorem()
        result = slice_proof(thm, Verbosity.NORMAL)
        assert all(not isinstance(prop, Axiom) for prop in result)

    def test_terse_slice_keeps_root_and_premise(self) -> None:
        thm = _build_theorem()
        result = slice_proof(thm, Verbosity.TERSE)
        assert result[0] == thm
        assert len(result) == 2
