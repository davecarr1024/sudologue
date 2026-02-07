"""Command-line interface for sudologue."""

import argparse
import sys
from pathlib import Path

from sudologue.model.board import Board
from sudologue.proof.proposition import Axiom, Elimination, Lemma
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.solver.solve_result import SolveResult, SolveStatus
from sudologue.solver.solver import Solver


def format_board(board: Board) -> str:
    """Render a board as a human-readable grid."""
    lines: list[str] = []
    box = int(board.size**0.5)
    for r in range(board.size):
        if r > 0 and r % box == 0:
            # Horizontal separator between box bands
            sep = "+".join("-" * (box * 2 + 1) for _ in range(box))
            lines.append(sep)
        parts: list[str] = []
        for c in range(board.size):
            if c > 0 and c % box == 0:
                parts.append("|")
            val = board.cells[r][c]
            parts.append(str(val) if val is not None else ".")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def format_proof(result: SolveResult) -> str:
    """Render the solve trace as a human-readable proof."""
    lines: list[str] = []

    lines.append("Initial board:")
    lines.append(format_board(result.initial))
    lines.append("")

    for i, step in enumerate(result.steps, 1):
        thm = step.theorem
        lines.append(f"Step {i}: {thm} [{thm.rule}]")

        for premise in thm.premises:
            if isinstance(premise, Lemma):
                lines.append(f"  {premise}")
                for elim in premise.premises:
                    if isinstance(elim, Elimination):
                        axiom = elim.premises[0]
                        if isinstance(axiom, Axiom):
                            lines.append(
                                f"    {elim} because {axiom}" f" in {elim.house}"
                            )
        lines.append("")

    if result.status == SolveStatus.SOLVED:
        lines.append("Solved!")
    else:
        lines.append(f"Stuck: {result.diagnosis}")

    lines.append(format_board(result.final_board))
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sudologue",
        description="Sudoku solver with proof-based reasoning",
    )
    parser.add_argument(
        "puzzle",
        nargs="?",
        help="Puzzle string (0 = empty cell)",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Read puzzle from file (first non-empty line)",
    )
    parser.add_argument(
        "--size",
        "-s",
        type=int,
        default=9,
        help="Board size (default: 9)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    puzzle: str | None = args.puzzle

    if args.file is not None:
        file_path: Path = args.file
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            return 1
        text = file_path.read_text()
        # Use first non-empty line as puzzle string
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                puzzle = stripped
                break

    if puzzle is None:
        parser.print_help()
        return 1

    size: int = args.size

    try:
        board = Board.from_string(puzzle, size=size)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    solver = Solver([NakedSingle()])
    result = solver.solve(board)

    print(format_proof(result))

    return 0 if result.status == SolveStatus.SOLVED else 1


if __name__ == "__main__":
    sys.exit(main())
