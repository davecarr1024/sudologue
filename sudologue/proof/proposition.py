from dataclasses import dataclass

from sudologue.model.cell import Cell
from sudologue.model.house import House


@dataclass(frozen=True)
class Axiom:
    """A given value observed on the board. No premises."""

    cell: Cell
    value: int

    def __str__(self) -> str:
        return f"{self.cell} = {self.value}"


@dataclass(frozen=True)
class Elimination:
    """Cell cannot contain value because of a placed value in a shared house."""

    cell: Cell
    value: int
    house: House
    premises: tuple[Axiom, ...]

    def __str__(self) -> str:
        return f"{self.cell} ≠ {self.value}"


@dataclass(frozen=True)
class Lemma:
    """Remaining possible values for a cell after all eliminations."""

    cell: Cell
    domain: frozenset[int]
    premises: tuple[Elimination, ...]

    def __str__(self) -> str:
        values = sorted(self.domain)
        return f"domain of {self.cell} = {{{', '.join(str(v) for v in values)}}}"


@dataclass(frozen=True)
class Theorem:
    """A proven placement backed by a proof chain."""

    cell: Cell
    value: int
    rule: str
    premises: tuple[Lemma, ...]

    def __str__(self) -> str:
        return f"place {self.value} at {self.cell}"


Proposition = Axiom | Elimination | Lemma | Theorem
