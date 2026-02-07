from dataclasses import dataclass

from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import all_houses
from sudologue.proof.proposition import Axiom, Elimination, Lemma, RangeLemma


@dataclass(frozen=True)
class Derivation:
    """All propositions derived from a board state in a single pass."""

    size: int
    axioms: tuple[Axiom, ...]
    eliminations: tuple[Elimination, ...]
    lemmas: tuple[Lemma, ...]
    range_lemmas: tuple[RangeLemma, ...]


def derive(board: Board) -> Derivation:
    """Eagerly derive all axioms, eliminations, domain lemmas, and range lemmas."""
    axioms = _extract_axioms(board)
    axiom_by_cell: dict[Cell, Axiom] = {ax.cell: ax for ax in axioms}
    eliminations = _derive_eliminations(board, axiom_by_cell)
    lemmas = _derive_lemmas(board, eliminations)
    range_lemmas = _derive_ranges(board, eliminations)
    return Derivation(
        size=board.size,
        axioms=axioms,
        eliminations=eliminations,
        lemmas=lemmas,
        range_lemmas=range_lemmas,
    )


def _extract_axioms(board: Board) -> tuple[Axiom, ...]:
    """Produce an axiom for each placed value on the board."""
    result: list[Axiom] = []
    for r in range(board.size):
        for c in range(board.size):
            val = board.cells[r][c]
            if val is not None:
                result.append(Axiom(Cell(r, c), val))
    return tuple(result)


def _derive_eliminations(
    board: Board, axiom_by_cell: dict[Cell, Axiom]
) -> tuple[Elimination, ...]:
    """For each axiom, eliminate its value from all empty peer cells."""
    seen: set[tuple[int, int, int]] = set()
    result: list[Elimination] = []

    for house in all_houses(board.size):
        for cell in house.cells:
            axiom = axiom_by_cell.get(cell)
            if axiom is None:
                continue
            for peer in house.cells:
                if peer == cell:
                    continue
                if board.value_at(peer) is not None:
                    continue
                key = (peer.row, peer.col, axiom.value)
                if key in seen:
                    continue
                seen.add(key)
                result.append(Elimination(peer, axiom.value, house, (axiom,)))

    return tuple(result)


def _derive_lemmas(
    board: Board, eliminations: tuple[Elimination, ...]
) -> tuple[Lemma, ...]:
    """For each empty cell, compute its domain from eliminations."""
    elims_by_cell: dict[Cell, list[Elimination]] = {}
    for elim in eliminations:
        elims_by_cell.setdefault(elim.cell, []).append(elim)

    full_domain = frozenset(range(1, board.size + 1))
    result: list[Lemma] = []

    for cell in board.empty_cells:
        cell_elims = elims_by_cell.get(cell, [])
        eliminated_values = frozenset(e.value for e in cell_elims)
        domain = full_domain - eliminated_values
        result.append(Lemma(cell, domain, tuple(cell_elims)))

    return tuple(result)


def _derive_ranges(
    board: Board, eliminations: tuple[Elimination, ...]
) -> tuple[RangeLemma, ...]:
    """For each house and value, compute the remaining candidate cells."""
    elim_by_cell_value: dict[tuple[Cell, int], Elimination] = {
        (elim.cell, elim.value): elim for elim in eliminations
    }
    result: list[RangeLemma] = []

    for house in all_houses(board.size):
        empty_cells = [cell for cell in house.cells if board.value_at(cell) is None]
        if not empty_cells:
            continue
        for value in range(1, board.size + 1):
            cells: list[Cell] = []
            premises: list[Elimination] = []
            for cell in empty_cells:
                elim = elim_by_cell_value.get((cell, value))
                if elim is None:
                    cells.append(cell)
                else:
                    premises.append(elim)
            result.append(RangeLemma(house, value, tuple(cells), tuple(premises)))

    return tuple(result)
