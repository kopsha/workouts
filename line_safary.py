from collections import namedtuple

Position = namedtuple("Position", ["row", "col"])
GridStep = namedtuple("GridStep", ["act", "pos"])


def show(grid, expected=None):
    print("Grid")
    print("\n".join(grid))
    if expected is not None:
        print("must be", expected)
    return grid


def find_path_ends(grid):
    cols = len(grid[0])
    flat = "".join(grid)
    fx1 = flat.find("X")
    assert fx1 >= 0, "Cannot find any X"
    fx2 = flat.find("X", fx1 + 1)
    assert fx2 >= 0, "Cannot find second X"

    start = Position(*divmod(fx1, cols))
    end = Position(*divmod(fx2, cols))

    return start, end


def add_grid_padding(grid):
    cols = len(grid[0])

    empty_row = " " * (cols + 2)
    padded_grid = list()
    padded_grid.append(empty_row)
    for row in grid:
        padded_row = " " + row + " "
        padded_grid.append(padded_row)
    padded_grid.append(empty_row)

    return padded_grid


def neighbours(grid, pos, skip):
    row, col = pos.row, pos.col
    result = {
        GridStep(grid[row + y][col + x], Position(row + y, col + x))
        for y, x in [(-1, 0), (0, -1), (0, 1), (1, 0)]
        if grid[row + y][col + x] != " " and Position(row + y, col + x) not in skip
    }
    return result


def has_valid_line_ordered(grid, reverse=False):
    padded_grid = add_grid_padding(grid)
    show(padded_grid)

    start, end = find_path_ends(padded_grid)
    if reverse:
        start, end = end, start

    visited = set()
    previous, current = None, GridStep("X", start)

    while current and current.pos != end:
        # print(".", current)
        visited.add(current.pos)

        valid_moves = list()
        for move in neighbours(padded_grid, current.pos, skip=visited):
            if current.act == "X":
                if move.pos.row == current.pos.row and move.act in {"-", "X", "+"}:
                    valid_moves.append(move)
                elif move.pos.col == current.pos.col and move.act in {"|", "X", "+"}:
                    valid_moves.append(move)
            elif current.act == "-":
                if move.pos.row == current.pos.row and move.act in {"-", "X", "+"}:
                    valid_moves.append(move)
            elif current.act == "|":
                if move.pos.col == current.pos.col and move.act in {"|", "X", "+"}:
                    valid_moves.append(move)
            elif current.act == "+":
                if (
                    previous.pos.row != move.pos.row
                    and previous.pos.col != move.pos.col
                ):
                    valid_moves.append(move)

        # print(f"\t{valid_moves=}")

        if len(valid_moves) != 1:
            # print(f"Expected a single valid move, {valid_moves=}")
            return False

        next_step = valid_moves.pop()
        previous, current = current, next_step

    visited.add(current.pos)

    # check if there are leftovers
    for row, row_content in enumerate(padded_grid):
        for col, mark in enumerate(row_content):
            pos = Position(row, col)
            if mark != " " and pos not in visited:
                # print(f"Leftovers found: {mark=}, {pos=}")
                return False

    return True


def has_valid_line(grid):
    if has_valid_line_ordered(grid, reverse=False):
        return True

    return has_valid_line_ordered(grid, reverse=True)


def test_line_safari():
    grid = ["X-----|----X"]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["           ", "X---------X", "           ", "           "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["     ", "  X  ", "  |  ", "  |  ", "  X  "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "                    ",
        "     +--------+     ",
        "  X--+        +--+  ",
        "                 |  ",
        "                 X  ",
        "                    ",
    ]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "                     ",
        "    +-------------+  ",
        "    |             |  ",
        " X--+      X------+  ",
        "                     ",
    ]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "                      ",
        "   +-------+          ",
        "   |      +++---+     ",
        "X--+      +-+   X     ",
    ]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "   |--------+    ",
        "X---        ---+ ",
        "               | ",
        "               X ",
    ]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "              ",
        "   +------    ",
        "   |          ",
        "X--+      X   ",
        "              ",
    ]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "      +------+",
        "      |      |",
        "X-----+------+",
        "      |       ",
        "      X       ",
    ]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [" X  ", " |  ", " +  ", " X  "]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [
        "X-----+",
        "      |",
        "X-----+",
        "      |",
        "------+",
    ]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected
    grid = [
        "     X        ",
        "     |   |    ",
        " +   |  -+-   ",
        "     |   |    ",
        "     X        ",
    ]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected
