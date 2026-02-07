"""Command-line interface for sudologue."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from sudologue.model.board import Board
from sudologue.model.house import HouseType
from sudologue.narration.policy import Verbosity
from sudologue.proof.identity import prop_id
from sudologue.proof.minimizer import slice_proof
from sudologue.proof.proposition import (
    Axiom,
    Elimination,
    EliminationPremise,
    Lemma,
    RangeLemma,
)
from sudologue.proof.rules.hidden_single import HiddenSingle
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.solver.solve_result import SolveResult, SolveStatus
from sudologue.solver.solver import Solver


def _format_cells(cells: tuple[object, ...]) -> str:
    return ", ".join(str(cell) for cell in cells)


def _format_elimination_reason(
    elim: Elimination, reasons: Sequence[EliminationPremise]
) -> str | None:
    if not reasons:
        return None

    if len(reasons) == 1 and isinstance(reasons[0], Axiom):
        return f"because {reasons[0]} in {elim.house}"

    if all(isinstance(reason, RangeLemma) for reason in reasons):
        range_reasons = [reason for reason in reasons if isinstance(reason, RangeLemma)]
        if any(reason.value != elim.value for reason in range_reasons):
            return "because " + "; ".join(str(reason) for reason in reasons)
        houses = {reason.house for reason in range_reasons}
        cells_sets = {reason.cells for reason in range_reasons}
        values = sorted({reason.value for reason in range_reasons})

        if len(range_reasons) == 1:
            reason = range_reasons[0]
            cells = _format_cells(reason.cells)
            if reason.house != elim.house:
                if (
                    reason.house.house_type == HouseType.BOX
                    and elim.house.house_type in {HouseType.ROW, HouseType.COLUMN}
                ):
                    return (
                        f"because in {reason.house}, {reason.value} is confined to "
                        f"{{{cells}}} in {elim.house}, so eliminate {reason.value} "
                        f"from the rest of {elim.house} outside {reason.house}"
                    )
                if (
                    reason.house.house_type in {HouseType.ROW, HouseType.COLUMN}
                    and elim.house.house_type == HouseType.BOX
                ):
                    return (
                        f"because in {reason.house}, {reason.value} is confined to "
                        f"{{{cells}}} in {elim.house}, so eliminate {reason.value} "
                        f"from the rest of {elim.house} outside {reason.house}"
                    )
            if elim.cell not in reason.cells:
                return f"because {reason} excludes {elim.cell}"

        if len(houses) == 1 and len(cells_sets) == 1:
            house = next(iter(houses))
            cells = _format_cells(next(iter(cells_sets)))
            values_text = ", ".join(str(value) for value in values)
            return (
                f"because in {house}, only {{{values_text}}} fit in "
                f"{{{cells}}}, so other digits are eliminated from those cells"
            )

    if all(isinstance(reason, Lemma) for reason in reasons):
        lemma_reasons = [reason for reason in reasons if isinstance(reason, Lemma)]
        if any(elim.value not in reason.domain for reason in lemma_reasons):
            return "because " + "; ".join(str(reason) for reason in reasons)
        domains = {reason.domain for reason in lemma_reasons}
        if len(domains) == 1:
            domain = next(iter(domains))
            if len(domain) == 2:
                values_text = ", ".join(str(value) for value in sorted(domain))
                cells = _format_cells(tuple(reason.cell for reason in lemma_reasons))
                return (
                    f"because in {elim.house}, {{{cells}}} have domain "
                    f"{{{values_text}}}, so eliminate those digits from other cells"
                )

    return "because " + "; ".join(str(reason) for reason in reasons)


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


def format_proof(result: SolveResult, verbosity: Verbosity = Verbosity.FULL) -> str:
    """Render the solve trace as a human-readable proof."""
    lines: list[str] = []

    lines.append("Initial board:")
    lines.append(format_board(result.initial))
    lines.append("")

    for i, step in enumerate(result.steps, 1):
        thm = step.theorem
        lines.append(f"Step {i}: {thm} [{thm.rule}]")

        if verbosity == Verbosity.TERSE:
            lines.append("")
            continue

        slice_ids = {prop_id(prop) for prop in slice_proof(thm, verbosity)}

        for premise in thm.premises:
            if prop_id(premise) not in slice_ids:
                continue
            lines.append(f"  {premise}")
            for elim in premise.premises:
                if prop_id(elim) not in slice_ids:
                    continue
                reasons = [
                    reason for reason in elim.premises if prop_id(reason) in slice_ids
                ]
                reason_text = _format_elimination_reason(elim, reasons)
                if reason_text is None:
                    lines.append(f"    {elim}")
                else:
                    lines.append(f"    {elim} {reason_text}")
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

    solver = Solver([NakedSingle(), HiddenSingle()])
    result = solver.solve(board)

    print(format_proof(result))

    return 0 if result.status == SolveStatus.SOLVED else 1


if __name__ == "__main__":
    sys.exit(main())
