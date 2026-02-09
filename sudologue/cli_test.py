"""Tests for the CLI module."""

from pathlib import Path

from sudologue.cli import format_board, format_elimination_reason, format_proof, main
from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import HouseType, all_houses
from sudologue.narration.policy import Verbosity
from sudologue.proof.proposition import Axiom, Elimination, RangeLemma
from sudologue.proof.rules.hidden_single import HiddenSingle
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
        # Should contain range and elimination details
        assert "range" in text
        assert "because" in text

    def test_terse_output(self) -> None:
        board = Board.from_string("1230341221434321", size=4)
        result = Solver([NakedSingle()]).solve(board)
        text = format_proof(result, verbosity=Verbosity.TERSE)
        assert "Step 1:" in text
        assert "domain" not in text
        assert "because" not in text

    def test_normal_output(self) -> None:
        board = Board.from_string("1230341221434321", size=4)
        result = Solver([NakedSingle()]).solve(board)
        text = format_proof(result, verbosity=Verbosity.NORMAL)
        assert "Step 1:" in text
        assert "≠" in text
        # NORMAL excludes axioms, so elimination reasons (axioms) are filtered
        # and eliminations are shown without "because" annotations
        assert "Solved!" in text

    def test_pointing_claiming_output(self) -> None:
        # This puzzle requires pointing/claiming to solve
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
        result = Solver([NakedSingle(), HiddenSingle()]).solve(board)
        text = format_proof(result)
        assert "Solved!" in text
        # Should contain pointing/claiming narration
        assert "confined to" in text or "because" in text


def _row0_4x4():
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.ROW and h.index == 0
    )


def _box0_4x4():
    return next(
        h for h in all_houses(4) if h.house_type == HouseType.BOX and h.index == 0
    )


class TestFormatEliminationReason:
    def test_no_reasons_returns_none(self) -> None:
        elim = Elimination(Cell(0, 1), 1, _row0_4x4(), (Axiom(Cell(0, 0), 1),))
        assert format_elimination_reason(elim, []) is None

    def test_single_axiom_reason(self) -> None:
        ax = Axiom(Cell(0, 0), 1)
        elim = Elimination(Cell(0, 1), 1, _row0_4x4(), (ax,))
        result = format_elimination_reason(elim, [ax])
        assert result is not None
        assert "because" in result
        assert "row 0" in result

    def test_pointing_box_to_row(self) -> None:
        # A RangeLemma from a box confining a value to a row
        box = _box0_4x4()
        row = _row0_4x4()
        rl = RangeLemma(box, 1, (Cell(0, 0), Cell(0, 1)), ())
        elim = Elimination(Cell(0, 2), 1, row, (rl,))
        result = format_elimination_reason(elim, [rl])
        assert result is not None
        assert "confined to" in result

    def test_claiming_row_to_box(self) -> None:
        # A RangeLemma from a row confining a value to a box
        row = _row0_4x4()
        box = _box0_4x4()
        rl = RangeLemma(row, 1, (Cell(0, 0), Cell(0, 1)), ())
        elim = Elimination(Cell(1, 0), 1, box, (rl,))
        result = format_elimination_reason(elim, [rl])
        assert result is not None
        assert "confined to" in result

    def test_range_excludes_cell(self) -> None:
        # RangeLemma from same house where target cell is not in range
        row = _row0_4x4()
        rl = RangeLemma(row, 1, (Cell(0, 2), Cell(0, 3)), ())
        elim = Elimination(Cell(0, 0), 1, row, (rl,))
        result = format_elimination_reason(elim, [rl])
        assert result is not None
        assert "excludes" in result

    def test_range_value_mismatch_fallback(self) -> None:
        # RangeLemma with a different value than the elimination
        row = _row0_4x4()
        rl = RangeLemma(row, 2, (Cell(0, 1),), ())
        elim = Elimination(Cell(0, 0), 1, row, (rl,))
        result = format_elimination_reason(elim, [rl])
        assert result is not None
        assert "because" in result

    def test_fallback_for_mixed_premise_types(self) -> None:
        # Mix of Axiom and RangeLemma (neither all-RangeLemma nor all-Lemma)
        ax = Axiom(Cell(0, 0), 1)
        row = _row0_4x4()
        rl = RangeLemma(row, 1, (Cell(0, 1),), ())
        elim = Elimination(Cell(0, 2), 1, row, (ax, rl))
        result = format_elimination_reason(elim, [ax, rl])
        assert result is not None
        assert "because" in result


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
