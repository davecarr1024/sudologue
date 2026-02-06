"""Full board solve tests for easy puzzles (solvable with singles only)."""

from sudologue.inference.inference import Placement
from sudologue.inference.solve_result import SolveStatus
from sudologue.model.board import Board
from sudologue.rules.hidden_single import HiddenSingle
from sudologue.rules.naked_single import NakedSingle
from sudologue.solver.solver import Solver


def _make_solver() -> Solver:
    return Solver(rules=[NakedSingle(), HiddenSingle()])


class TestEasyPuzzles:
    def test_one_cell_missing(self) -> None:
        """Trivial: one cell missing, solved by naked single."""
        puzzle = (
            "534678912"
            "672195348"
            "198342567"
            "859761423"
            "426853791"
            "713924856"
            "961537284"
            "287419635"
            "345286170"
        )
        solver = _make_solver()
        result = solver.solve(Board.from_string(puzzle))
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 1
        assert isinstance(result.steps[0].inference.action, Placement)
        assert result.steps[0].inference.action.value == 9

    def test_two_cells_missing(self) -> None:
        """Two cells missing, both naked singles."""
        puzzle = (
            "534678912"
            "672195348"
            "198342567"
            "859761423"
            "426853791"
            "713924856"
            "961537284"
            "287419635"
            "345286100"
        )
        solver = _make_solver()
        result = solver.solve(Board.from_string(puzzle))
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 2

    def test_wikipedia_puzzle(self) -> None:
        """Classic easy puzzle from Wikipedia's sudoku article."""
        puzzle = (
            "530070000"
            "600195000"
            "098000060"
            "800060003"
            "400803001"
            "700020006"
            "060000280"
            "000419005"
            "000080079"
        )
        expected_solution = (
            "534678912"
            "672195348"
            "198342567"
            "859761423"
            "426853791"
            "713924856"
            "961537284"
            "287419635"
            "345286179"
        )
        solver = _make_solver()
        result = solver.solve(Board.from_string(puzzle))
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.is_complete
        # Verify the solution matches.
        expected = Board.from_string(expected_solution)
        assert result.final_board.cells == expected.cells

    def test_every_step_has_valid_board(self) -> None:
        """Each intermediate board state should pass invariant checks."""
        puzzle = (
            "530070000"
            "600195000"
            "098000060"
            "800060003"
            "400803001"
            "700020006"
            "060000280"
            "000419005"
            "000080079"
        )
        solver = _make_solver()
        result = solver.solve(Board.from_string(puzzle))
        # Board invariants are checked on construction, so if we got here
        # without a BoardError, every step produced a valid board.
        assert result.status == SolveStatus.SOLVED
        for step in result.steps:
            # Double-check: no None values where we placed something.
            action = step.inference.action
            if isinstance(action, Placement):
                assert step.board.value_at(action.cell) == action.value

    def test_trace_uses_simplest_rule(self) -> None:
        """Naked singles should be preferred over hidden singles."""
        puzzle = (
            "534678912"
            "672195348"
            "198342567"
            "859761423"
            "426853791"
            "713924856"
            "961537284"
            "287419635"
            "345286170"
        )
        solver = _make_solver()
        result = solver.solve(Board.from_string(puzzle))
        # This puzzle has a naked single, so it should use that rule.
        assert result.steps[0].inference.rule == "Naked Single"

    def test_easy_puzzle_002(self) -> None:
        """Another easy puzzle solvable with singles."""
        puzzle = (
            "003020600"
            "900305001"
            "001806400"
            "008102900"
            "700000008"
            "006708200"
            "002609500"
            "800203009"
            "005010300"
        )
        solver = _make_solver()
        result = solver.solve(Board.from_string(puzzle))
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.is_complete
