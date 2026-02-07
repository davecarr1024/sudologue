from typing import Sequence

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

        for range_lemma in derivation.range_lemmas:
            if len(range_lemma.cells) == 1:
                target = range_lemma.cells[0]
                results.append(
                    Theorem(target, range_lemma.value, self.name, (range_lemma,))
                )

        return results
