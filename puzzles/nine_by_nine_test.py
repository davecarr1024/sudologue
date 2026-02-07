"""End-to-end tests: 9x9 solves using both hidden and naked singles."""

from sudologue.model.board import Board
from sudologue.proof.rules.hidden_single import HiddenSingle
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.solver.solve_result import SolveStatus
from sudologue.solver.solver import Solver


class TestNineByNineSingles:
    def test_solve_with_hidden_and_naked_singles(self) -> None:
        # Puzzle derived from a valid 9x9 grid; solvable via singles.
        puzzle = (
            "020406000"
            "450009023"
            "080120050"
            "004067801"
            "007800230"
            "890000007"
            "040070012"
            "008912300"
            "912005008"
        )
        board = Board.from_string(puzzle, size=9)
        result = Solver([NakedSingle(), HiddenSingle()]).solve(board)
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.is_complete
        rules = {step.theorem.rule for step in result.steps}
        assert "naked single" in rules
        assert "hidden single" in rules
