from sudologue.model.cell import Cell
from sudologue.model.house import HouseType, all_houses
from sudologue.proof.identity import collect_proof, dedupe_propositions, prop_id
from sudologue.proof.proposition import (
    Axiom,
    Candidate,
    Elimination,
    Lemma,
    RangeLemma,
    Theorem,
)


def _row0_4x4():
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.ROW and h.index == 0
    )


def _col3_4x4():
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.COLUMN and h.index == 3
    )


class TestPropId:
    def test_same_conclusion_same_id(self) -> None:
        ax1 = Axiom(Cell(0, 0), 1)
        ax2 = Axiom(Cell(0, 0), 1)
        assert prop_id(ax1) == prop_id(ax2)

    def test_theorem_ignores_rule(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        thm1 = Theorem(Cell(2, 3), 4, "naked single", (lemma,))
        thm2 = Theorem(Cell(2, 3), 4, "hidden single", (lemma,))
        assert prop_id(thm1) == prop_id(thm2)

    def test_range_lemma_id_stable(self) -> None:
        house = _row0_4x4()
        rl1 = RangeLemma(house, 2, (Cell(0, 1), Cell(0, 2)), ())
        rl2 = RangeLemma(house, 2, (Cell(0, 1), Cell(0, 2)), ())
        assert prop_id(rl1) == prop_id(rl2)

    def test_candidate_id_stable(self) -> None:
        lemma = Lemma(Cell(2, 3), frozenset({4}), ())
        c1 = Candidate(Cell(2, 3), 4, (lemma,))
        c2 = Candidate(Cell(2, 3), 4, (lemma,))
        assert prop_id(c1) == prop_id(c2)


class TestIndexing:
    def test_dedupe_prefers_first_instance(self) -> None:
        ax1 = Axiom(Cell(0, 0), 1)
        ax2 = Axiom(Cell(0, 0), 1)
        deduped = dedupe_propositions([ax1, ax2])
        assert deduped == (ax1,)


class TestCollectProof:
    def test_collects_unique_chain(self) -> None:
        ax1 = Axiom(Cell(0, 3), 1)
        ax2 = Axiom(Cell(1, 3), 2)
        ax3 = Axiom(Cell(2, 0), 3)
        e1 = Elimination(Cell(2, 3), 1, _col3_4x4(), (ax1,))
        e2 = Elimination(Cell(2, 3), 2, _col3_4x4(), (ax2,))
        e3 = Elimination(Cell(2, 3), 3, _row0_4x4(), (ax3,))
        lemma = Lemma(Cell(2, 3), frozenset({4}), (e1, e2, e3))
        theorem = Theorem(Cell(2, 3), 4, "naked single", (lemma,))

        proof = collect_proof(theorem)
        assert len(proof) == 8
        assert theorem in proof
        assert lemma in proof
        assert ax1 in proof
        assert ax2 in proof
        assert ax3 in proof

    def test_shared_premise_deduplicates(self) -> None:
        """Two eliminations sharing an axiom should not duplicate it in the proof."""
        ax = Axiom(Cell(0, 0), 1)
        row = _row0_4x4()
        e1 = Elimination(Cell(0, 1), 1, row, (ax,))
        e2 = Elimination(Cell(0, 2), 1, row, (ax,))
        lemma = Lemma(Cell(0, 3), frozenset({4}), (e1, e2))
        theorem = Theorem(Cell(0, 3), 4, "naked single", (lemma,))

        proof = collect_proof(theorem)
        # theorem + lemma + e1 + e2 + ax (shared, counted once) = 5
        assert len(proof) == 5
        axiom_count = sum(1 for p in proof if isinstance(p, Axiom))
        assert axiom_count == 1
