from collections.abc import Sequence
from typing import Protocol

from sudologue.inference.inference import Inference
from sudologue.model.board import Board


class Rule(Protocol):
    """A sudoku solving rule that can deduce inferences from a board state."""

    @property
    def name(self) -> str: ...

    def apply(self, board: Board) -> Sequence[Inference]: ...
