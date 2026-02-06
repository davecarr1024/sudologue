from sudologue.model.cell import Cell
from sudologue.model.house import (
    ALL_HOUSES,
    HouseType,
    houses_for,
    peers,
)


class TestAllHouses:
    def test_total_count(self) -> None:
        assert len(ALL_HOUSES) == 27

    def test_row_count(self) -> None:
        rows = [h for h in ALL_HOUSES if h.house_type == HouseType.ROW]
        assert len(rows) == 9

    def test_column_count(self) -> None:
        cols = [h for h in ALL_HOUSES if h.house_type == HouseType.COLUMN]
        assert len(cols) == 9

    def test_box_count(self) -> None:
        boxes = [h for h in ALL_HOUSES if h.house_type == HouseType.BOX]
        assert len(boxes) == 9

    def test_each_house_has_9_cells(self) -> None:
        for house in ALL_HOUSES:
            assert len(house.cells) == 9, f"{house} has {len(house.cells)} cells"

    def test_row_0_cells(self) -> None:
        row_0 = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.ROW and h.index == 0
        )
        assert all(c.row == 0 for c in row_0.cells)
        assert {c.col for c in row_0.cells} == set(range(9))

    def test_column_0_cells(self) -> None:
        col_0 = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.COLUMN and h.index == 0
        )
        assert all(c.col == 0 for c in col_0.cells)
        assert {c.row for c in col_0.cells} == set(range(9))

    def test_box_0_cells(self) -> None:
        box_0 = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.BOX and h.index == 0
        )
        expected = {Cell(r, c) for r in range(3) for c in range(3)}
        assert set(box_0.cells) == expected

    def test_box_4_center(self) -> None:
        box_4 = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.BOX and h.index == 4
        )
        expected = {Cell(r, c) for r in range(3, 6) for c in range(3, 6)}
        assert set(box_4.cells) == expected

    def test_box_8_bottom_right(self) -> None:
        box_8 = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.BOX and h.index == 8
        )
        expected = {Cell(r, c) for r in range(6, 9) for c in range(6, 9)}
        assert set(box_8.cells) == expected


class TestHousesFor:
    def test_returns_three_houses(self) -> None:
        houses = houses_for(Cell(0, 0))
        assert len(houses) == 3

    def test_contains_all_types(self) -> None:
        houses = houses_for(Cell(4, 5))
        types = {h.house_type for h in houses}
        assert types == {HouseType.ROW, HouseType.COLUMN, HouseType.BOX}

    def test_correct_row(self) -> None:
        houses = houses_for(Cell(3, 7))
        row = next(h for h in houses if h.house_type == HouseType.ROW)
        assert row.index == 3

    def test_correct_column(self) -> None:
        houses = houses_for(Cell(3, 7))
        col = next(h for h in houses if h.house_type == HouseType.COLUMN)
        assert col.index == 7

    def test_correct_box(self) -> None:
        houses = houses_for(Cell(3, 7))
        box = next(h for h in houses if h.house_type == HouseType.BOX)
        # Row 3, col 7 -> box (3//3)*3 + (7//3) = 1*3 + 2 = 5
        assert box.index == 5


class TestPeers:
    def test_count_is_20(self) -> None:
        assert len(peers(Cell(0, 0))) == 20

    def test_count_center(self) -> None:
        assert len(peers(Cell(4, 4))) == 20

    def test_excludes_self(self) -> None:
        cell = Cell(3, 3)
        assert cell not in peers(cell)

    def test_includes_same_row(self) -> None:
        p = peers(Cell(0, 0))
        for c in range(1, 9):
            assert Cell(0, c) in p

    def test_includes_same_col(self) -> None:
        p = peers(Cell(0, 0))
        for r in range(1, 9):
            assert Cell(r, 0) in p

    def test_includes_same_box(self) -> None:
        p = peers(Cell(0, 0))
        assert Cell(1, 1) in p
        assert Cell(1, 2) in p
        assert Cell(2, 1) in p
        assert Cell(2, 2) in p

    def test_excludes_unrelated(self) -> None:
        p = peers(Cell(0, 0))
        # Cell(5, 5) shares no house with (0, 0)
        assert Cell(5, 5) not in p


class TestHouseStr:
    def test_row_str(self) -> None:
        row = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.ROW and h.index == 0
        )
        assert str(row) == "row 1"

    def test_column_str(self) -> None:
        col = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.COLUMN and h.index == 4
        )
        assert str(col) == "column 5"

    def test_box_str(self) -> None:
        box = next(
            h for h in ALL_HOUSES if h.house_type == HouseType.BOX and h.index == 8
        )
        assert str(box) == "box 9"
