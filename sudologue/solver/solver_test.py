import pytest

from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import HouseType, all_houses
from sudologue.proof.identity import collect_proof
from sudologue.proof.proposition import Axiom, Elimination, Lemma, RangeLemma, Theorem
from sudologue.proof.rules.hidden_single import HiddenSingle
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.proof.scoring import proof_size
from sudologue.solver.solve_result import SolveStatus, SolveStep
from sudologue.solver.solver import Solver


class TestSolveResult:
    def test_final_board_with_steps(self) -> None:
        board = Board.from_string("1230000000000000", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        # (0,3) should be placed as 4
        assert result.final_board.value_at(Cell(0, 3)) == 4

    def test_final_board_no_steps(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        assert result.final_board is board

    def test_frozen(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        with pytest.raises(AttributeError):
            result.status = SolveStatus.STUCK  # type: ignore[misc]


class TestSolverSingleStep:
    def test_one_forced_cell(self) -> None:
        # Row 0 has 1,2,3 -> (0,3) must be 4
        board = Board.from_string("1230000000000000", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        # Should have at least one step placing 4 at (0,3)
        step_cells = {s.theorem.cell for s in result.steps}
        assert Cell(0, 3) in step_cells

    def test_step_has_theorem_and_board(self) -> None:
        board = Board.from_string("1230000000000000", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        step = result.steps[0]
        assert step.theorem.cell == Cell(0, 3)
        assert step.theorem.value == 4
        assert step.board.value_at(Cell(0, 3)) == 4


class TestSolverStuck:
    def test_empty_board_stuck(self) -> None:
        # Empty board with naked single only -> stuck immediately
        board = Board.from_string("0000000000000000", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        assert result.status == SolveStatus.STUCK
        assert result.diagnosis is not None
        assert "16 empty cells" in result.diagnosis

    def test_no_rules_always_stuck(self) -> None:
        board = Board.from_string("1230000000000000", size=4)
        solver = Solver([])
        result = solver.solve(board)
        assert result.status == SolveStatus.STUCK

    def test_stuck_preserves_initial_board(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        assert result.initial is board


class TestSolverAlreadySolved:
    def test_complete_board_returns_solved(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 0


class TestSolverMultiStep:
    def test_cascade_placements(self) -> None:
        # A board where placing one value reveals another naked single
        # 123_ / ___4 / ___1 / ___3
        # (0,3) forced to 4, then each step may reveal more
        board = Board.from_string("1230000400010003", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        # Should make progress (at least place 4 at (0,3))
        assert len(result.steps) > 0
        first = result.steps[0]
        assert first.theorem.rule == "naked single"

    def test_each_step_validates_board(self) -> None:
        """Every intermediate board in the solve trace is valid."""
        board = Board.from_string("1230000400010003", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        for step in result.steps:
            # Board construction validates invariants, so if we got here
            # without an exception, the board is valid.
            assert step.board.size == 4


class TestSolverProofInspection:
    """Verify that theorems in the solve trace have inspectable proof chains."""

    def test_all_theorems_have_premises(self) -> None:
        board = Board.from_string("1230000400010003", size=4)
        solver = Solver([NakedSingle()])
        result = solver.solve(board)
        for step in result.steps:
            thm = step.theorem
            assert len(thm.premises) > 0
            range_lemma = thm.premises[0]
            assert isinstance(range_lemma, RangeLemma)
            assert range_lemma.cells == () or range_lemma.cells == (thm.cell,)


class TestSolverScoring:
    def test_scorer_prefers_smaller_proof(self) -> None:
        house = next(
            h for h in all_houses(4) if h.house_type == HouseType.ROW and h.index == 0
        )
        ax1 = Axiom(Cell(0, 0), 1)
        ax2 = Axiom(Cell(0, 1), 2)
        ax3 = Axiom(Cell(0, 2), 3)
        e1 = Elimination(Cell(0, 3), 1, house, (ax1,))
        e2 = Elimination(Cell(0, 3), 2, house, (ax2,))
        e3 = Elimination(Cell(0, 3), 3, house, (ax3,))

        lemma_short = Lemma(Cell(0, 3), frozenset({4}), ())
        lemma_long = Lemma(Cell(0, 3), frozenset({4}), (e1, e2, e3))

        thm_short = Theorem(Cell(0, 3), 4, "stub", (lemma_short,))
        thm_long = Theorem(Cell(0, 3), 4, "stub", (lemma_long,))

        class StubRule:
            @property
            def name(self) -> str:
                return "stub"

            def apply(self, derivation: object) -> list[Theorem]:
                return [thm_long, thm_short]

        board = Board.from_string("1230341221434321", size=4)
        solver = Solver([StubRule()], scorer=proof_size)
        result = solver.solve(board)
        assert result.steps[0].theorem is thm_short


class TestSolverPointingClaiming:
    def test_pointing_pair_used_in_solve(self) -> None:
        board = Board.from_string("1234000021430320", size=4)
        solver = Solver([HiddenSingle(), NakedSingle()])
        result = solver.solve(board)
        assert result.status == SolveStatus.SOLVED

        def uses_pointing(step: SolveStep) -> bool:
            theorem = step.theorem
            for prop in collect_proof(theorem):
                if isinstance(prop, Elimination):
                    if prop.house.house_type in {HouseType.ROW, HouseType.COLUMN}:
                        for premise in prop.premises:
                            if (
                                isinstance(premise, RangeLemma)
                                and premise.house.house_type == HouseType.BOX
                            ):
                                return True
            return False

        assert any(uses_pointing(step) for step in result.steps)

    def test_claiming_used_in_solve(self) -> None:
        puzzle = (
            "004678010"
            "670195340"
            "108300567"
            "850760400"
            "420003700"
            "010020056"
            "961037284"
            "287410000"
            "040286100"
        )
        board = Board.from_string(puzzle, size=9)
        solver = Solver([HiddenSingle(), NakedSingle()])
        result = solver.solve(board)
        assert result.status == SolveStatus.SOLVED

        def uses_claiming(step: SolveStep) -> bool:
            theorem = step.theorem
            for prop in collect_proof(theorem):
                if isinstance(prop, Elimination):
                    if prop.house.house_type == HouseType.BOX:
                        for premise in prop.premises:
                            if isinstance(
                                premise, RangeLemma
                            ) and premise.house.house_type in {
                                HouseType.ROW,
                                HouseType.COLUMN,
                            }:
                                return True
            return False

        assert any(uses_claiming(step) for step in result.steps)
