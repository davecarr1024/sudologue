import pytest

from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.solver.solve_result import SolveStatus
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
            lemma = thm.premises[0]
            assert thm.value in lemma.domain or len(lemma.domain) == 1
