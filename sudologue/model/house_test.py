import pytest

from sudologue.model.cell import Cell
from sudologue.model.house import House, HouseType, all_houses, houses_for, peers


class TestHouseConstruction:
    def test_create_row(self) -> None:
        cells = tuple(Cell(0, c) for c in range(4))
        house = House(HouseType.ROW, 0, cells)
        assert house.house_type == HouseType.ROW
        assert house.index == 0
        assert len(house.cells) == 4

    def test_str(self) -> None:
        cells = tuple(Cell(0, c) for c in range(4))
        assert str(House(HouseType.ROW, 0, cells)) == "row 0"
        assert str(House(HouseType.COLUMN, 2, cells)) == "column 2"
        assert str(House(HouseType.BOX, 1, cells)) == "box 1"

    def test_frozen(self) -> None:
        cells = tuple(Cell(0, c) for c in range(4))
        house = House(HouseType.ROW, 0, cells)
        with pytest.raises(AttributeError):
            house.index = 1  # type: ignore[misc]


class TestAllHouses4x4:
    def test_count(self) -> None:
        houses = all_houses(4)
        assert len(houses) == 12  # 4 rows + 4 cols + 4 boxes

    def test_row_cells(self) -> None:
        houses = all_houses(4)
        rows = [h for h in houses if h.house_type == HouseType.ROW]
        assert len(rows) == 4
        assert rows[0].cells == (Cell(0, 0), Cell(0, 1), Cell(0, 2), Cell(0, 3))
        assert rows[2].cells == (Cell(2, 0), Cell(2, 1), Cell(2, 2), Cell(2, 3))

    def test_column_cells(self) -> None:
        houses = all_houses(4)
        cols = [h for h in houses if h.house_type == HouseType.COLUMN]
        assert len(cols) == 4
        assert cols[0].cells == (Cell(0, 0), Cell(1, 0), Cell(2, 0), Cell(3, 0))
        assert cols[3].cells == (Cell(0, 3), Cell(1, 3), Cell(2, 3), Cell(3, 3))

    def test_box_cells(self) -> None:
        houses = all_houses(4)
        boxes = [h for h in houses if h.house_type == HouseType.BOX]
        assert len(boxes) == 4
        # Box 0: top-left 2x2
        assert boxes[0].cells == (Cell(0, 0), Cell(0, 1), Cell(1, 0), Cell(1, 1))
        # Box 1: top-right 2x2
        assert boxes[1].cells == (Cell(0, 2), Cell(0, 3), Cell(1, 2), Cell(1, 3))
        # Box 2: bottom-left 2x2
        assert boxes[2].cells == (Cell(2, 0), Cell(2, 1), Cell(3, 0), Cell(3, 1))
        # Box 3: bottom-right 2x2
        assert boxes[3].cells == (Cell(2, 2), Cell(2, 3), Cell(3, 2), Cell(3, 3))

    def test_every_cell_in_exactly_three_houses(self) -> None:
        houses = all_houses(4)
        for r in range(4):
            for c in range(4):
                cell = Cell(r, c)
                containing = [h for h in houses if cell in h.cells]
                assert len(containing) == 3, f"{cell} in {len(containing)} houses"

    def test_each_house_has_size_cells(self) -> None:
        for house in all_houses(4):
            assert len(house.cells) == 4


class TestAllHouses9x9:
    def test_count(self) -> None:
        houses = all_houses(9)
        assert len(houses) == 27  # 9 rows + 9 cols + 9 boxes

    def test_every_cell_in_exactly_three_houses(self) -> None:
        houses = all_houses(9)
        for r in range(9):
            for c in range(9):
                cell = Cell(r, c)
                containing = [h for h in houses if cell in h.cells]
                assert len(containing) == 3, f"{cell} in {len(containing)} houses"

    def test_each_house_has_nine_cells(self) -> None:
        for house in all_houses(9):
            assert len(house.cells) == 9


class TestInvalidSize:
    def test_non_perfect_square(self) -> None:
        with pytest.raises(ValueError, match="perfect square"):
            all_houses(5)

    def test_size_six(self) -> None:
        with pytest.raises(ValueError, match="perfect square"):
            all_houses(6)


class TestHousesFor:
    def test_corner_cell(self) -> None:
        containing = houses_for(Cell(0, 0), 4)
        types = {h.house_type for h in containing}
        assert types == {HouseType.ROW, HouseType.COLUMN, HouseType.BOX}

    def test_correct_houses(self) -> None:
        containing = houses_for(Cell(2, 3), 4)
        assert len(containing) == 3
        row = next(h for h in containing if h.house_type == HouseType.ROW)
        col = next(h for h in containing if h.house_type == HouseType.COLUMN)
        box = next(h for h in containing if h.house_type == HouseType.BOX)
        assert row.index == 2
        assert col.index == 3
        assert box.index == 3  # bottom-right box


class TestPeers:
    def test_peer_count_4x4(self) -> None:
        # In 4x4, each cell has: 3 row peers + 3 col peers + 3 box peers
        # minus overlaps. Corner cell (0,0): row {01,02,03} + col {10,20,30}
        # + box {01,10,11} = {01,02,03,10,20,30,11} = 7
        p = peers(Cell(0, 0), 4)
        assert len(p) == 7

    def test_peer_count_9x9(self) -> None:
        # In 9x9, each cell has exactly 20 peers
        p = peers(Cell(4, 4), 9)
        assert len(p) == 20

    def test_does_not_include_self(self) -> None:
        cell = Cell(1, 1)
        p = peers(cell, 4)
        assert cell not in p

    def test_peer_symmetry(self) -> None:
        a = Cell(0, 0)
        b = Cell(0, 1)
        assert b in peers(a, 4)
        assert a in peers(b, 4)

    def test_non_peer(self) -> None:
        # (0,0) and (3,3) are in different rows, cols, and boxes on 4x4
        # Box 0 = {(0,0),(0,1),(1,0),(1,1)}, Box 3 = {(2,2),(2,3),(3,2),(3,3)}
        assert Cell(3, 3) not in peers(Cell(0, 0), 4)
