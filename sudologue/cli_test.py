"""Tests for the CLI module."""

from pathlib import Path

from sudologue.cli import format_board, format_proof, main
from sudologue.model.board import Board
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.solver.solver import Solver


class TestFormatBoard:
    def test_4x4_empty(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        text = format_board(board)
        lines = text.splitlines()
        assert len(lines) == 5  # 4 rows + 1 separator
        assert "." in lines[0]

    def test_4x4_full(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        text = format_board(board)
        assert "1" in text
        assert "." not in text

    def test_4x4_separator(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        text = format_board(board)
        lines = text.splitlines()
        # Row separator between rows 1 and 2
        assert "+" in lines[2] or "-" in lines[2]

    def test_4x4_box_divider(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        text = format_board(board)
        lines = text.splitlines()
        # Data rows should have | between box columns
        assert "|" in lines[0]


class TestFormatProof:
    def test_solved_output(self) -> None:
        board = Board.from_string("1230341221434321", size=4)
        result = Solver([NakedSingle()]).solve(board)
        text = format_proof(result)
        assert "Initial board:" in text
        assert "Step 1:" in text
        assert "naked single" in text
        assert "Solved!" in text

    def test_stuck_output(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        result = Solver([NakedSingle()]).solve(board)
        text = format_proof(result)
        assert "Stuck:" in text

    def test_no_steps_solved(self) -> None:
        board = Board.from_string("1234341221434321", size=4)
        result = Solver([NakedSingle()]).solve(board)
        text = format_proof(result)
        assert "Step 1:" not in text
        assert "Solved!" in text

    def test_proof_chain_details(self) -> None:
        board = Board.from_string("1230341221434321", size=4)
        result = Solver([NakedSingle()]).solve(board)
        text = format_proof(result)
        # Should contain domain and elimination details
        assert "domain" in text
        assert "because" in text


class TestMainCli:
    def test_puzzle_string(self, capsys: object) -> None:
        exit_code = main(["--size", "4", "1230341221434321"])
        assert exit_code == 0

    def test_stuck_returns_1(self) -> None:
        exit_code = main(["--size", "4", "0000000000000000"])
        assert exit_code == 1

    def test_no_args_returns_1(self) -> None:
        exit_code = main([])
        assert exit_code == 1

    def test_invalid_puzzle_returns_1(self) -> None:
        exit_code = main(["--size", "4", "12"])
        assert exit_code == 1

    def test_file_input(self, tmp_path: Path) -> None:
        puzzle_file = tmp_path / "puzzle.txt"
        puzzle_file.write_text("1230341221434321\n")
        exit_code = main(["--size", "4", "--file", str(puzzle_file)])
        assert exit_code == 0

    def test_file_not_found(self) -> None:
        exit_code = main(["--size", "4", "--file", "/nonexistent/path.txt"])
        assert exit_code == 1

    def test_file_skips_blank_lines(self, tmp_path: Path) -> None:
        puzzle_file = tmp_path / "puzzle.txt"
        puzzle_file.write_text("\n\n1230341221434321\n")
        exit_code = main(["--size", "4", "--file", str(puzzle_file)])
        assert exit_code == 0

    def test_default_size_is_9(self) -> None:
        # A wrong-length string for size 9 should fail
        exit_code = main(["1230341221434321"])
        assert exit_code == 1
