from typing import Sequence

from sudologue.proof.engine import Derivation
from sudologue.proof.proposition import Theorem


class NakedSingle:
    """If a cell's domain has exactly one value, place it there."""

    @property
    def name(self) -> str:
        return "naked single"

    def apply(self, derivation: Derivation) -> Sequence[Theorem]:
        results: list[Theorem] = []
        for lemma in derivation.lemmas:
            if len(lemma.domain) == 1:
                (value,) = lemma.domain
                results.append(Theorem(lemma.cell, value, self.name, (lemma,)))
        return results
