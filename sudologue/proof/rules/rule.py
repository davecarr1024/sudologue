from typing import Protocol, Sequence

from sudologue.proof.engine import Derivation
from sudologue.proof.proposition import Theorem


class Rule(Protocol):
    """Protocol for theorem-producing inference rules."""

    @property
    def name(self) -> str: ...

    def apply(self, derivation: Derivation) -> Sequence[Theorem]: ...
