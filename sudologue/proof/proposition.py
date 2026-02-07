from dataclasses import dataclass

from sudologue.model.cell import Cell
from sudologue.model.house import House, HouseLike


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
    premises: tuple["EliminationPremise", ...]

    def __str__(self) -> str:
        return f"{self.cell} ≠ {self.value}"


NotCandidate = Elimination


@dataclass(frozen=True)
class RangeLemma:
    """Possible cells in a house for a value after eliminations."""

    house: HouseLike
    value: int
    cells: tuple[Cell, ...]
    premises: tuple[Elimination, ...]

    def __str__(self) -> str:
        cells = ", ".join(str(cell) for cell in self.cells)
        return f"range of {self.house} for {self.value} = {{{cells}}}"


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
class Candidate:
    """A possible value for a cell, derived from its domain lemma."""

    cell: Cell
    value: int
    premises: tuple[Lemma, ...]

    def __str__(self) -> str:
        return f"candidate {self.cell} = {self.value}"


@dataclass(frozen=True)
class Theorem:
    """A proven placement backed by a proof chain."""

    cell: Cell
    value: int
    rule: str
    premises: tuple["Premise", ...]

    def __str__(self) -> str:
        return f"place {self.value} at {self.cell}"


Premise = Lemma | RangeLemma
EliminationPremise = Axiom | Lemma | RangeLemma | Candidate
Proposition = Axiom | Elimination | RangeLemma | Lemma | Candidate | Theorem
