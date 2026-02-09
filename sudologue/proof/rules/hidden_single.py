from typing import Sequence

from sudologue.model.house import HouseType
from sudologue.proof.engine import Derivation
from sudologue.proof.proposition import Theorem


class HiddenSingle:
    """If a value appears in only one domain within a house, place it there."""

    @property
    def name(self) -> str:
        return "hidden single"

    def apply(self, derivation: Derivation) -> Sequence[Theorem]:
        results: list[Theorem] = []
        if not derivation.range_lemmas:
            return results

        seen: set[tuple[int, int, int]] = set()
        for range_lemma in derivation.range_lemmas:
            if range_lemma.house.house_type == HouseType.CELL:
                continue
            if len(range_lemma.cells) == 1:
                target = range_lemma.cells[0]
                key = (target.row, target.col, range_lemma.value)
                if key in seen:
                    continue
                seen.add(key)
                results.append(
                    Theorem(target, range_lemma.value, self.name, (range_lemma,))
                )

        return results
