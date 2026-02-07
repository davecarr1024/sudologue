from collections.abc import Callable, Sequence

from sudologue.model.board import Board
from sudologue.proof.engine import derive
from sudologue.proof.proposition import Theorem
from sudologue.proof.rules.rule import Rule
from sudologue.solver.solve_result import SolveResult, SolveStatus, SolveStep


class Solver:
    """Solve loop: derive propositions, search for theorems, place values."""

    def __init__(
        self, rules: Sequence[Rule], scorer: Callable[[Theorem], int] | None = None
    ) -> None:
        self._rules = list(rules)
        self._scorer = scorer

    def solve(self, board: Board) -> SolveResult:
        steps: list[SolveStep] = []
        current = board

        while not current.is_complete:
            derivation = derive(current)
            theorem = None

            for rule in self._rules:
                theorems = rule.apply(derivation)
                if theorems:
                    if self._scorer is None:
                        theorem = theorems[0]
                    else:
                        theorem = min(theorems, key=self._scorer)
                    break

            if theorem is None:
                empty_count = len(current.empty_cells)
                return SolveResult(
                    initial=board,
                    steps=tuple(steps),
                    status=SolveStatus.STUCK,
                    diagnosis=f"{empty_count} empty cells remaining",
                )

            new_board = current.place(theorem.cell, theorem.value)
            steps.append(SolveStep(theorem=theorem, board=new_board))
            current = new_board

        return SolveResult(
            initial=board,
            steps=tuple(steps),
            status=SolveStatus.SOLVED,
        )
