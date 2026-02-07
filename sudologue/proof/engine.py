from dataclasses import dataclass

from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.model.house import House, HouseType, all_houses
from sudologue.proof.proposition import Axiom, Candidate, Elimination, Lemma, RangeLemma


@dataclass(frozen=True)
class Derivation:
    """All propositions derived from a board state in a single pass."""

    size: int
    axioms: tuple[Axiom, ...]
    eliminations: tuple[Elimination, ...]
    lemmas: tuple[Lemma, ...]
    range_lemmas: tuple[RangeLemma, ...]
    candidates: tuple[Candidate, ...]


def derive(board: Board) -> Derivation:
    """Eagerly derive all axioms, eliminations, domain lemmas, and range lemmas."""
    axioms = _extract_axioms(board)
    axiom_by_cell: dict[Cell, Axiom] = {ax.cell: ax for ax in axioms}
    eliminations = _derive_eliminations(board, axiom_by_cell)
    lemmas: tuple[Lemma, ...] = ()
    range_lemmas: tuple[RangeLemma, ...] = ()

    while True:
        lemmas = _derive_lemmas(board, eliminations)
        range_lemmas = _derive_ranges(board, eliminations)
        pair_elims = _derive_pair_eliminations(
            board.size, lemmas, range_lemmas, eliminations
        )
        point_elims = _derive_pointing_eliminations(
            board.size, lemmas, range_lemmas, eliminations + pair_elims
        )
        new_elims = pair_elims + point_elims
        if not new_elims:
            break
        eliminations = eliminations + new_elims

    candidates = _derive_candidates(lemmas)
    return Derivation(
        size=board.size,
        axioms=axioms,
        eliminations=eliminations,
        lemmas=lemmas,
        range_lemmas=range_lemmas,
        candidates=candidates,
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


def _derive_pair_eliminations(
    size: int,
    lemmas: tuple[Lemma, ...],
    range_lemmas: tuple[RangeLemma, ...],
    eliminations: tuple[Elimination, ...],
) -> tuple[Elimination, ...]:
    """Derive eliminations from naked/hidden pair patterns."""
    existing_keys = {(elim.cell, elim.value) for elim in eliminations}
    lemmas_by_cell = {lemma.cell: lemma for lemma in lemmas}
    results: list[Elimination] = []

    if size == 0:
        return tuple(results)

    # Naked pairs
    for house in all_houses(size):
        house_lemmas = [
            lemmas_by_cell[cell] for cell in house.cells if cell in lemmas_by_cell
        ]
        pairs: dict[frozenset[int], list[Lemma]] = {}
        for lemma in house_lemmas:
            if len(lemma.domain) == 2:
                pairs.setdefault(lemma.domain, []).append(lemma)

        for values, pair_lemmas in pairs.items():
            if len(pair_lemmas) != 2:
                continue
            for lemma in house_lemmas:
                if lemma in pair_lemmas:
                    continue
                for value in values:
                    key = (lemma.cell, value)
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)
                    results.append(
                        Elimination(lemma.cell, value, house, tuple(pair_lemmas))
                    )

    # Hidden pairs
    range_by_house: dict[House, list[RangeLemma]] = {}
    for range_lemma in range_lemmas:
        if len(range_lemma.cells) == 2:
            range_by_house.setdefault(range_lemma.house, []).append(range_lemma)

    for house, house_ranges in range_by_house.items():
        by_cells: dict[tuple[Cell, ...], list[RangeLemma]] = {}
        for range_lemma in house_ranges:
            by_cells.setdefault(range_lemma.cells, []).append(range_lemma)

        for cells, ranges in by_cells.items():
            if len(ranges) != 2:
                continue
            pair_values = {ranges[0].value, ranges[1].value}
            for cell in cells:
                lemma = lemmas_by_cell.get(cell)
                if lemma is None:
                    continue
                for value in lemma.domain:
                    if value in pair_values:
                        continue
                    key = (cell, value)
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)
                    results.append(Elimination(cell, value, house, tuple(ranges)))

    return tuple(results)


def _derive_pointing_eliminations(
    size: int,
    lemmas: tuple[Lemma, ...],
    range_lemmas: tuple[RangeLemma, ...],
    eliminations: tuple[Elimination, ...],
) -> tuple[Elimination, ...]:
    """Derive eliminations from pointing pairs and box-line reductions."""
    if size == 0:
        return ()

    existing_keys = {(elim.cell, elim.value) for elim in eliminations}
    lemmas_by_cell = {lemma.cell: lemma for lemma in lemmas}
    results: list[Elimination] = []

    houses = all_houses(size)
    row_houses = {h.index: h for h in houses if h.house_type == HouseType.ROW}
    col_houses = {h.index: h for h in houses if h.house_type == HouseType.COLUMN}
    box_houses = {h.index: h for h in houses if h.house_type == HouseType.BOX}

    box_size = int(size**0.5)

    def box_index(cell: Cell) -> int:
        return (cell.row // box_size) * box_size + (cell.col // box_size)

    # Pointing: box -> row/column
    for range_lemma in range_lemmas:
        if range_lemma.house.house_type != HouseType.BOX or not range_lemma.cells:
            continue
        rows = {cell.row for cell in range_lemma.cells}
        cols = {cell.col for cell in range_lemma.cells}

        if len(rows) == 1:
            row_idx = next(iter(rows))
            row_house = row_houses[row_idx]
            for cell in row_house.cells:
                if cell in range_lemma.cells or cell not in lemmas_by_cell:
                    continue
                key = (cell, range_lemma.value)
                if key in existing_keys:
                    continue
                existing_keys.add(key)
                results.append(
                    Elimination(cell, range_lemma.value, row_house, (range_lemma,))
                )

        if len(cols) == 1:
            col_idx = next(iter(cols))
            col_house = col_houses[col_idx]
            for cell in col_house.cells:
                if cell in range_lemma.cells or cell not in lemmas_by_cell:
                    continue
                key = (cell, range_lemma.value)
                if key in existing_keys:
                    continue
                existing_keys.add(key)
                results.append(
                    Elimination(cell, range_lemma.value, col_house, (range_lemma,))
                )

    # Claiming: row/column -> box
    for range_lemma in range_lemmas:
        if range_lemma.house.house_type not in {HouseType.ROW, HouseType.COLUMN}:
            continue
        if not range_lemma.cells:
            continue
        boxes = {box_index(cell) for cell in range_lemma.cells}
        if len(boxes) != 1:
            continue
        box_idx = next(iter(boxes))
        box_house = box_houses[box_idx]
        for cell in box_house.cells:
            if cell in range_lemma.cells or cell not in lemmas_by_cell:
                continue
            key = (cell, range_lemma.value)
            if key in existing_keys:
                continue
            existing_keys.add(key)
            results.append(
                Elimination(cell, range_lemma.value, box_house, (range_lemma,))
            )

    return tuple(results)


def derive_pointing_eliminations(
    size: int,
    lemmas: tuple[Lemma, ...],
    range_lemmas: tuple[RangeLemma, ...],
    eliminations: tuple[Elimination, ...],
) -> tuple[Elimination, ...]:
    """Public wrapper for testing pointing/claiming eliminations."""
    return _derive_pointing_eliminations(size, lemmas, range_lemmas, eliminations)


def _derive_candidates(lemmas: tuple[Lemma, ...]) -> tuple[Candidate, ...]:
    """Create candidate propositions from domain lemmas."""
    result: list[Candidate] = []
    for lemma in lemmas:
        for value in sorted(lemma.domain):
            result.append(Candidate(lemma.cell, value, (lemma,)))
    return tuple(result)
