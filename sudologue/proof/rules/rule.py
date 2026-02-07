from typing import Protocol, Sequence

from sudologue.proof.engine import Derivation
from sudologue.proof.proposition import Elimination, Theorem


class EliminationRule(Protocol):
    """Protocol for elimination-producing inference rules."""

    @property
    def name(self) -> str: ...

    def apply(self, derivation: Derivation) -> Sequence[Elimination]: ...


class SelectionRule(Protocol):
    """Protocol for theorem-producing selection rules."""

    @property
    def name(self) -> str: ...

    def apply(self, derivation: Derivation) -> Sequence[Theorem]: ...
