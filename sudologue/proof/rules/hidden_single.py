from typing import Sequence

from sudologue.model.house import all_houses
from sudologue.proof.engine import Derivation
from sudologue.proof.proposition import Theorem


class HiddenSingle:
    """If a value appears in only one domain within a house, place it there."""

    @property
    def name(self) -> str:
        return "hidden single"

    def apply(self, derivation: Derivation) -> Sequence[Theorem]:
        results: list[Theorem] = []
        if not derivation.lemmas:
            return results

        lemmas_by_cell = {lemma.cell: lemma for lemma in derivation.lemmas}
        size = derivation.size

        for house in all_houses(size):
            house_lemmas = [
                lemmas_by_cell[cell] for cell in house.cells if cell in lemmas_by_cell
            ]
            if not house_lemmas:
                continue

            for value in range(1, size + 1):
                candidates = [lemma for lemma in house_lemmas if value in lemma.domain]
                if len(candidates) == 1:
                    target = candidates[0]
                    results.append(
                        Theorem(target.cell, value, self.name, tuple(house_lemmas))
                    )

        return results
