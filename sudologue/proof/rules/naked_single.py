from typing import Sequence

from sudologue.model.house import HouseType
from sudologue.proof.engine import Derivation
from sudologue.proof.proposition import RangeLemma, Theorem


class NakedSingle:
    """If a cell's range in its cell-house yields one value, place it there."""

    @property
    def name(self) -> str:
        return "naked single"

    def apply(self, derivation: Derivation) -> Sequence[Theorem]:
        results: list[Theorem] = []
        ranges_by_cell: dict[object, list[RangeLemma]] = {}

        for range_lemma in derivation.range_lemmas:
            if range_lemma.house.house_type != HouseType.CELL:
                continue
            ranges_by_cell.setdefault(range_lemma.house, []).append(range_lemma)

        for _house, ranges in ranges_by_cell.items():
            candidates = [rl for rl in ranges if rl.cells]
            if len(candidates) != 1:
                continue
            chosen = candidates[0]
            excluded = tuple(rl for rl in ranges if not rl.cells)
            premises = excluded or (chosen,)
            results.append(Theorem(chosen.cells[0], chosen.value, self.name, premises))

        return results
