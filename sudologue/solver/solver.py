from collections.abc import Sequence

from sudologue.inference.inference import Inference, Placement
from sudologue.inference.solve_result import SolveResult, SolveStatus, TraceStep
from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.rules.rule import Rule


class Solver:
    """Applies rules in priority order to solve a board, one step at a time."""

    def __init__(self, rules: Sequence[Rule] | None = None) -> None:
        self._rules: tuple[Rule, ...] = tuple(rules) if rules else ()

    def solve(self, board: Board) -> SolveResult:
        """Solve the board by repeatedly applying rules.

        Returns a SolveResult with SOLVED status if all cells are filled,
        or STUCK with a diagnosis if no rule can make progress.
        """
        steps: list[TraceStep] = []
        current = board

        while not current.is_complete:
            inference = self._find_inference(current)
            if inference is None:
                empty = sum(
                    1
                    for r in range(9)
                    for c in range(9)
                    if current.value_at(Cell(r, c)) is None
                )
                return SolveResult(
                    initial=board,
                    steps=tuple(steps),
                    status=SolveStatus.STUCK,
                    diagnosis=f"{empty} cells remaining, no rule can make progress",
                )

            current = self._apply_inference(current, inference)
            steps.append(TraceStep(inference=inference, board=current))

        return SolveResult(
            initial=board,
            steps=tuple(steps),
            status=SolveStatus.SOLVED,
        )

    def _find_inference(self, board: Board) -> Inference | None:
        for rule in self._rules:
            inferences = rule.apply(board)
            if inferences:
                return inferences[0]
        return None

    def _apply_inference(self, board: Board, inference: Inference) -> Board:
        action = inference.action
        if isinstance(action, Placement):
            return board.place(action.cell, action.value)
        # action is Elimination
        current = board
        for cell in action.cells:
            current = current.eliminate(cell, action.values)
        return current
