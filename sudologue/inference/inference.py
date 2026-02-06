from dataclasses import dataclass

from sudologue.model.cell import Cell
from sudologue.model.house import House


@dataclass(frozen=True, slots=True)
class Evidence:
    """Structured record of what a rule observed.

    The description is a terse, mechanical summary for debugging.
    Narrators produce the real prose from the structured fields.
    """

    focus_cells: tuple[Cell, ...]
    focus_house: House | None
    focus_digit: int | None
    candidates_seen: frozenset[int] | None
    description: str


@dataclass(frozen=True, slots=True)
class Placement:
    """Place a value in a cell."""

    cell: Cell
    value: int


@dataclass(frozen=True, slots=True)
class Elimination:
    """Remove candidate values from one or more cells."""

    cells: tuple[Cell, ...]
    values: frozenset[int]


@dataclass(frozen=True, slots=True)
class Inference:
    """A single deductive step.

    Records which rule fired, what it concluded (place a value or
    eliminate candidates), and the structured evidence for why.
    """

    rule: str
    action: Placement | Elimination
    evidence: Evidence
