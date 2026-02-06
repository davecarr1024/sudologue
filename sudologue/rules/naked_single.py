from collections.abc import Sequence

from sudologue.inference.inference import Evidence, Inference, Placement
from sudologue.model.board import Board
from sudologue.model.cell import Cell


class NakedSingle:
    """A cell has exactly one candidate remaining. It must be that value."""

    @property
    def name(self) -> str:
        return "Naked Single"

    def apply(self, board: Board) -> Sequence[Inference]:
        inferences: list[Inference] = []
        for row in range(9):
            for col in range(9):
                cell = Cell(row, col)
                candidates = board.candidates_at(cell)
                if len(candidates) == 1:
                    (value,) = candidates
                    inferences.append(
                        Inference(
                            rule=self.name,
                            action=Placement(cell=cell, value=value),
                            evidence=Evidence(
                                focus_cells=(cell,),
                                focus_house=None,
                                focus_digit=value,
                                candidates_seen=candidates,
                                description=f"{cell} has only one candidate: {value}",
                            ),
                        )
                    )
        return inferences
