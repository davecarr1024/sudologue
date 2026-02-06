import pytest

from sudologue.inference.inference import (
    Elimination,
    Evidence,
    Inference,
    Placement,
)
from sudologue.model.cell import Cell


class TestEvidence:
    def test_creation(self) -> None:
        ev = Evidence(
            focus_cells=(Cell(0, 0),),
            focus_house=None,
            focus_digit=5,
            candidates_seen=frozenset({5}),
            description="test",
        )
        assert ev.focus_digit == 5
        assert ev.description == "test"
        assert ev.focus_house is None

    def test_frozen(self) -> None:
        ev = Evidence(
            focus_cells=(Cell(0, 0),),
            focus_house=None,
            focus_digit=5,
            candidates_seen=frozenset({5}),
            description="test",
        )
        with pytest.raises(AttributeError):
            ev.description = "modified"  # type: ignore[misc]


class TestPlacement:
    def test_creation(self) -> None:
        p = Placement(cell=Cell(0, 0), value=5)
        assert p.cell == Cell(0, 0)
        assert p.value == 5

    def test_equality(self) -> None:
        assert Placement(Cell(0, 0), 5) == Placement(Cell(0, 0), 5)
        assert Placement(Cell(0, 0), 5) != Placement(Cell(0, 0), 6)


class TestElimination:
    def test_creation(self) -> None:
        e = Elimination(cells=(Cell(0, 0), Cell(0, 1)), values=frozenset({3, 7}))
        assert len(e.cells) == 2
        assert e.values == frozenset({3, 7})


class TestInference:
    def test_with_placement(self) -> None:
        inf = Inference(
            rule="Test Rule",
            action=Placement(cell=Cell(0, 0), value=5),
            evidence=Evidence(
                focus_cells=(Cell(0, 0),),
                focus_house=None,
                focus_digit=5,
                candidates_seen=frozenset({5}),
                description="test",
            ),
        )
        assert inf.rule == "Test Rule"
        assert isinstance(inf.action, Placement)

    def test_with_elimination(self) -> None:
        inf = Inference(
            rule="Test Rule",
            action=Elimination(cells=(Cell(0, 0),), values=frozenset({3})),
            evidence=Evidence(
                focus_cells=(Cell(0, 0),),
                focus_house=None,
                focus_digit=3,
                candidates_seen=None,
                description="test",
            ),
        )
        assert isinstance(inf.action, Elimination)

    def test_frozen(self) -> None:
        inf = Inference(
            rule="Test",
            action=Placement(cell=Cell(0, 0), value=1),
            evidence=Evidence(
                focus_cells=(Cell(0, 0),),
                focus_house=None,
                focus_digit=1,
                candidates_seen=frozenset({1}),
                description="test",
            ),
        )
        with pytest.raises(AttributeError):
            inf.rule = "Modified"  # type: ignore[misc]
