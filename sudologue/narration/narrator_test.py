from sudologue.inference.inference import Evidence, Inference, Placement
from sudologue.inference.solve_result import SolveResult, SolveStatus, TraceStep
from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.narration.narrator import DefaultNarrator

SOLUTION = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)

ONE_MISSING = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286170"
)


def _make_solved_result() -> SolveResult:
    initial = Board.from_string(ONE_MISSING)
    final = Board.from_string(SOLUTION)
    inference = Inference(
        rule="Naked Single",
        action=Placement(cell=Cell(8, 8), value=9),
        evidence=Evidence(
            focus_cells=(Cell(8, 8),),
            focus_house=None,
            focus_digit=9,
            candidates_seen=frozenset({9}),
            description="R9C9 has only one candidate: 9",
        ),
    )
    return SolveResult(
        initial=initial,
        steps=(TraceStep(inference=inference, board=final),),
        status=SolveStatus.SOLVED,
    )


class TestDefaultNarrator:
    def test_narrate_solved(self) -> None:
        narrator = DefaultNarrator()
        result = _make_solved_result()
        text = narrator.narrate(result)
        assert "Solved in 1 steps" in text
        assert "[Naked Single]" in text
        assert "R9C9" in text

    def test_narrate_stuck(self) -> None:
        narrator = DefaultNarrator()
        board = Board.from_string("." * 81)
        result = SolveResult(
            initial=board,
            steps=(),
            status=SolveStatus.STUCK,
            diagnosis="81 cells remaining",
        )
        text = narrator.narrate(result)
        assert "Stuck" in text
        assert "81 cells remaining" in text

    def test_narrate_step(self) -> None:
        narrator = DefaultNarrator()
        result = _make_solved_result()
        step_text = narrator.narrate_step(result.steps[0], 1)
        assert step_text.startswith("Step 1:")
        assert "[Naked Single]" in step_text
