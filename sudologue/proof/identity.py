from collections.abc import Iterable

from sudologue.proof.proposition import (
    Axiom,
    Candidate,
    Elimination,
    Lemma,
    Proposition,
    RangeLemma,
    Theorem,
)

PropId = tuple[object, ...]


def prop_id(prop: Proposition) -> PropId:
    if isinstance(prop, Axiom):
        return ("Axiom", prop.cell.row, prop.cell.col, prop.value)
    if isinstance(prop, Elimination):
        return ("Elimination", prop.cell.row, prop.cell.col, prop.value)
    if isinstance(prop, Lemma):
        return ("Lemma", prop.cell.row, prop.cell.col, tuple(sorted(prop.domain)))
    if isinstance(prop, RangeLemma):
        cells = tuple((cell.row, cell.col) for cell in prop.cells)
        return (
            "RangeLemma",
            prop.house.house_type,
            prop.house.index,
            prop.value,
            cells,
        )
    if isinstance(prop, Candidate):
        return ("Candidate", prop.cell.row, prop.cell.col, prop.value)
    assert isinstance(prop, Theorem)
    return ("Theorem", prop.cell.row, prop.cell.col, prop.value)


def index_propositions(props: Iterable[Proposition]) -> dict[PropId, Proposition]:
    index: dict[PropId, Proposition] = {}
    for prop in props:
        pid = prop_id(prop)
        index.setdefault(pid, prop)
    return index


def dedupe_propositions(props: Iterable[Proposition]) -> tuple[Proposition, ...]:
    return tuple(index_propositions(props).values())


def collect_proof(root: Proposition) -> tuple[Proposition, ...]:
    ordered: list[Proposition] = []
    seen: set[PropId] = set()

    def visit(node: Proposition) -> None:
        pid = prop_id(node)
        if pid in seen:
            return
        seen.add(pid)
        ordered.append(node)
        premises = getattr(node, "premises", ())
        for premise in premises:
            visit(premise)

    visit(root)
    return tuple(ordered)
