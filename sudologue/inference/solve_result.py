from dataclasses import dataclass
from enum import Enum

from sudologue.inference.inference import Inference
from sudologue.model.board import Board


class SolveStatus(Enum):
    SOLVED = "solved"
    STUCK = "stuck"


@dataclass(frozen=True, slots=True)
class TraceStep:
    """A paired snapshot: the inference that was applied and the resulting board."""

    inference: Inference
    board: Board


@dataclass(frozen=True, slots=True)
class SolveResult:
    """The complete solve trace.

    Contains the starting board, every step, and whether the puzzle
    was solved or the solver got stuck (with a diagnosis).
    """

    initial: Board
    steps: tuple[TraceStep, ...]
    status: SolveStatus
    diagnosis: str | None = None

    @property
    def final_board(self) -> Board:
        """The board state after the last step, or the initial board if no steps."""
        if self.steps:
            return self.steps[-1].board
        return self.initial
