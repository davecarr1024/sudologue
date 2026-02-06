from sudologue.inference.inference import Evidence, Inference, Placement
from sudologue.inference.solve_result import SolveResult, SolveStatus, TraceStep
from sudologue.model.board import Board
from sudologue.model.cell import Cell

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


def _make_inference() -> Inference:
    return Inference(
        rule="Test",
        action=Placement(cell=Cell(0, 0), value=5),
        evidence=Evidence(
            focus_cells=(Cell(0, 0),),
            focus_house=None,
            focus_digit=5,
            candidates_seen=frozenset({5}),
            description="test",
        ),
    )


class TestSolveStatus:
    def test_solved(self) -> None:
        assert SolveStatus.SOLVED.value == "solved"

    def test_stuck(self) -> None:
        assert SolveStatus.STUCK.value == "stuck"


class TestTraceStep:
    def test_creation(self) -> None:
        board = Board.from_string(SOLUTION)
        inference = _make_inference()
        step = TraceStep(inference=inference, board=board)
        assert step.board is board
        assert step.inference is inference


class TestSolveResult:
    def test_solved_no_diagnosis(self) -> None:
        board = Board.from_string(SOLUTION)
        result = SolveResult(
            initial=board,
            steps=(),
            status=SolveStatus.SOLVED,
        )
        assert result.status == SolveStatus.SOLVED
        assert result.diagnosis is None

    def test_stuck_with_diagnosis(self) -> None:
        board = Board.from_string("." * 81)
        result = SolveResult(
            initial=board,
            steps=(),
            status=SolveStatus.STUCK,
            diagnosis="81 cells remaining",
        )
        assert result.status == SolveStatus.STUCK
        assert result.diagnosis == "81 cells remaining"

    def test_final_board_no_steps(self) -> None:
        board = Board.from_string(SOLUTION)
        result = SolveResult(initial=board, steps=(), status=SolveStatus.SOLVED)
        assert result.final_board is board

    def test_final_board_with_steps(self) -> None:
        initial = Board.from_string("." * 81)
        final = Board.from_string(SOLUTION)
        step = TraceStep(inference=_make_inference(), board=final)
        result = SolveResult(
            initial=initial,
            steps=(step,),
            status=SolveStatus.SOLVED,
        )
        assert result.final_board is final
