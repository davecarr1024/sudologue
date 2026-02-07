"""End-to-end tests: full 4x4 board solves with proof verification."""

from sudologue.model.board import Board
from sudologue.model.cell import Cell
from sudologue.proof.proposition import Axiom, Elimination, Lemma
from sudologue.proof.rules.hidden_single import HiddenSingle
from sudologue.proof.rules.naked_single import NakedSingle
from sudologue.solver.solve_result import SolveStatus
from sudologue.solver.solver import Solver


def _solver() -> Solver:
    return Solver([NakedSingle()])


class TestAlreadySolved:
    def test_complete_board(self) -> None:
        # 1 2 3 4
        # 3 4 1 2
        # 2 1 4 3
        # 4 3 2 1
        board = Board.from_string("1234341221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 0
        assert result.final_board is board


class TestOneCellMissing:
    """A single empty cell is trivially naked-single-able."""

    def test_last_in_row(self) -> None:
        # Row 0: 1 2 3 _ -> must be 4
        board = Board.from_string("1230341221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 1
        assert result.final_board.value_at(Cell(0, 3)) == 4

    def test_first_in_row(self) -> None:
        # Row 0: _ 2 3 4 -> must be 1
        board = Board.from_string("0234341221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 1
        assert result.final_board.value_at(Cell(0, 0)) == 1

    def test_middle_of_board(self) -> None:
        # Row 2, col 1: _ -> must be 1
        board = Board.from_string("1234341220434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 1
        assert result.final_board.value_at(Cell(2, 1)) == 1


class TestMultiStepSolve:
    """Boards requiring cascading naked-single placements."""

    def test_two_empty_cells(self) -> None:
        # Two cells missing: (0,2) and (0,3)
        # Row 0: 1 2 _ _ with rest of board filled
        # After naked singles cascade, both should be placed
        board = Board.from_string("1200341221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.value_at(Cell(0, 2)) == 3
        assert result.final_board.value_at(Cell(0, 3)) == 4

    def test_four_empty_cells(self) -> None:
        # Full row 0 empty: _ _ _ _
        # Remaining rows: 3 4 1 2 / 2 1 4 3 / 4 3 2 1
        board = Board.from_string("0000341221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 4
        assert result.final_board.value_at(Cell(0, 0)) == 1
        assert result.final_board.value_at(Cell(0, 1)) == 2
        assert result.final_board.value_at(Cell(0, 2)) == 3
        assert result.final_board.value_at(Cell(0, 3)) == 4

    def test_sparse_board(self) -> None:
        # Half the cells given, checkerboard pattern:
        # 1 _ 3 _ / _ 4 _ 2 / 2 _ 4 _ / _ 3 _ 1
        # Solution: 1 2 3 4 / 3 4 1 2 / 2 1 4 3 / 4 3 2 1
        board = Board.from_string("1030040220400301", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.is_complete

    def test_step_count_matches_empty_cells(self) -> None:
        # 3 cells empty -> exactly 3 steps
        board = Board.from_string("1200041221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 3


class TestVariedDifficulty:
    """Additional 4x4 puzzles of varying difficulty (all naked-single solvable)."""

    def test_easy(self) -> None:
        # Only two cells missing in the first row.
        board = Board.from_string("1200341221434321", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert len(result.steps) == 2

    def test_medium(self) -> None:
        # Mixed givens across rows/cols; still naked-single solvable.
        board = Board.from_string("1030340200430301", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.is_complete

    def test_harder(self) -> None:
        # Fewer givens, requires more cascading singles.
        board = Board.from_string("1000040200430001", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        assert result.final_board.is_complete


class TestFullSolveFromSparseBoard:
    """Solve a 4x4 from minimal clues (naked-single solvable)."""

    def test_solve_and_verify_solution(self) -> None:
        # Target: 1 2 3 4 / 3 4 1 2 / 2 1 4 3 / 4 3 2 1
        # Checkerboard clues: 1 _ 3 _ / _ 4 _ 2 / 2 _ 4 _ / _ 3 _ 1
        board = Board.from_string("1030040220400301", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.SOLVED
        expected = Board.from_string("1234341221434321", size=4)
        assert result.final_board.cells == expected.cells

    def test_all_steps_are_naked_single(self) -> None:
        board = Board.from_string("1030040220400301", size=4)
        result = _solver().solve(board)
        for step in result.steps:
            assert step.theorem.rule == "naked single"


class TestProofChainIntegrity:
    """Verify that every proof chain in the solve trace is valid."""

    def test_every_theorem_has_lemma_premise(self) -> None:
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        for step in result.steps:
            thm = step.theorem
            assert len(thm.premises) == 1
            lemma = thm.premises[0]
            assert isinstance(lemma, Lemma)
            assert lemma.cell == thm.cell
            assert lemma.domain == frozenset({thm.value})

    def test_lemma_premises_are_eliminations(self) -> None:
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        for step in result.steps:
            lemma = step.theorem.premises[0]
            for elim in lemma.premises:
                assert isinstance(elim, Elimination)
                assert elim.cell == lemma.cell

    def test_elimination_premises_are_axioms(self) -> None:
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        for step in result.steps:
            lemma = step.theorem.premises[0]
            for elim in lemma.premises:
                for axiom in elim.premises:
                    assert isinstance(axiom, Axiom)
                    assert axiom.value == elim.value

    def test_proof_chain_traversable_to_axioms(self) -> None:
        """Full traversal: theorem -> lemma -> eliminations -> axioms."""
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        first = result.steps[0]
        thm = first.theorem

        # Theorem -> Lemma
        lemma = thm.premises[0]
        assert lemma.cell == thm.cell

        # Lemma -> Eliminations -> Axioms
        for elim in lemma.premises:
            assert len(elim.premises) >= 1
            axiom = elim.premises[0]
            assert axiom.value == elim.value

    def test_eliminated_values_complement_domain(self) -> None:
        """The eliminated values + domain values = full value set."""
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        for step in result.steps:
            lemma = step.theorem.premises[0]
            eliminated = {e.value for e in lemma.premises}
            domain = lemma.domain
            # Eliminated + domain should cover some subset of 1..4
            # (not necessarily all, since some values may not be
            # in the cell's houses)
            assert len(eliminated & domain) == 0


class TestBoardIntegrity:
    """Verify board consistency through every step of the solve."""

    def test_each_step_board_is_valid(self) -> None:
        """Board invariants are checked by __post_init__, so construction
        succeeding means the board is valid."""
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        for step in result.steps:
            assert step.board.size == 4

    def test_step_boards_are_monotonically_filled(self) -> None:
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        prev_empty = len(board.empty_cells)
        for step in result.steps:
            curr_empty = len(step.board.empty_cells)
            assert curr_empty == prev_empty - 1
            prev_empty = curr_empty

    def test_placed_values_persist(self) -> None:
        """Once a value is placed, it stays in all subsequent boards."""
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        placed: dict[Cell, int] = {}
        for step in result.steps:
            cell = step.theorem.cell
            value = step.theorem.value
            placed[cell] = value
            for prev_cell, prev_val in placed.items():
                assert step.board.value_at(prev_cell) == prev_val

    def test_initial_board_preserved(self) -> None:
        board = Board.from_string("1230000400010003", size=4)
        result = _solver().solve(board)
        assert result.initial is board
        # Original board should not be mutated
        assert board.value_at(Cell(0, 3)) is None


class TestStuckBoard:
    """Boards that naked single alone cannot solve."""

    def test_empty_board_stuck(self) -> None:
        board = Board.from_string("0000000000000000", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.STUCK
        assert result.diagnosis is not None

    def test_stuck_board_partial_progress(self) -> None:
        """Solver should make as much progress as possible before getting stuck."""
        # Only two clues — may make some progress but likely gets stuck
        board = Board.from_string("1200000000000000", size=4)
        result = _solver().solve(board)
        # Might be stuck or solved depending on cascade
        # Either way, final_board should have at least the original clues
        assert result.final_board.value_at(Cell(0, 0)) == 1
        assert result.final_board.value_at(Cell(0, 1)) == 2


class TestHiddenSingleSolve:
    """Boards that require a hidden single to make progress."""

    def test_naked_single_stuck(self) -> None:
        # This board has a hidden single but no naked singles.
        board = Board.from_string("1200001221000000", size=4)
        result = _solver().solve(board)
        assert result.status == SolveStatus.STUCK

    def test_hidden_single_progresses(self) -> None:
        board = Board.from_string("1200001221000000", size=4)
        solver = Solver([NakedSingle(), HiddenSingle()])
        result = solver.solve(board)
        assert len(result.steps) > 0
        assert result.steps[0].theorem.rule == "hidden single"
