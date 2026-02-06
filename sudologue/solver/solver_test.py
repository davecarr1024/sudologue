from sudologue.inference.solve_result import SolveStatus
from sudologue.model.board import Board
from sudologue.solver.solver import Solver

PUZZLE = (
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

SOLUTION = (
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


class TestSolverNoRules:
    def test_already_solved(self) -> None:
        solver = Solver()
        board = Board.from_string(SOLUTION)
        result = solver.solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 0

    def test_stuck_on_unsolved(self) -> None:
        solver = Solver()
        board = Board.from_string(PUZZLE)
        result = solver.solve(board)
        assert result.status == SolveStatus.STUCK
        assert result.diagnosis is not None
        assert "cells remaining" in result.diagnosis

    def test_stuck_returns_initial_board(self) -> None:
        solver = Solver()
        board = Board.from_string(PUZZLE)
        result = solver.solve(board)
        assert result.initial is board
        assert result.final_board is board
