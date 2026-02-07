from dataclasses import dataclass
from enum import Enum

from sudologue.model.board import Board
from sudologue.proof.proposition import Theorem


class SolveStatus(Enum):
    SOLVED = "solved"
    STUCK = "stuck"


@dataclass(frozen=True)
class SolveStep:
    """A single solving step: the theorem proven and the resulting board."""

    theorem: Theorem
    board: Board


@dataclass(frozen=True)
class SolveResult:
    """Complete solve trace from initial board to final state."""

    initial: Board
    steps: tuple[SolveStep, ...]
    status: SolveStatus
    diagnosis: str | None = None

    @property
    def final_board(self) -> Board:
        if self.steps:
            return self.steps[-1].board
        return self.initial
