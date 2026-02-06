from collections.abc import Sequence

from sudologue.inference.inference import Evidence, Inference, Placement
from sudologue.model.board import Board
from sudologue.model.house import ALL_HOUSES


class HiddenSingle:
    """A value has exactly one possible cell within a house. It must go there."""

    @property
    def name(self) -> str:
        return "Hidden Single"

    def apply(self, board: Board) -> Sequence[Inference]:
        inferences: list[Inference] = []
        seen: set[tuple[int, int, int]] = set()  # (row, col, value) dedup

        for house in ALL_HOUSES:
            for digit in range(1, 10):
                possible_cells = [
                    cell for cell in house.cells if digit in board.candidates_at(cell)
                ]
                if len(possible_cells) == 1:
                    cell = possible_cells[0]
                    key = (cell.row, cell.col, digit)
                    if key in seen:
                        continue
                    seen.add(key)
                    inferences.append(
                        Inference(
                            rule=self.name,
                            action=Placement(cell=cell, value=digit),
                            evidence=Evidence(
                                focus_cells=(cell,),
                                focus_house=house,
                                focus_digit=digit,
                                candidates_seen=board.candidates_at(cell),
                                description=(
                                    f"In {house}, {digit} can only go in {cell}"
                                ),
                            ),
                        )
                    )
        return inferences
