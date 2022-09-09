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

    start = divmod(fx1, cols)
    end = divmod(fx2, cols)

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
    row, col = pos
    result = {
        (grid[row + y][col + x], (row + y, col + x))
        for y, x in [(-1, 0), (0, -1), (0, 1), (1, 0)]
        if grid[row + y][col + x] != " " and (row + y, col + x) not in skip
    }
    return result


def has_valid_line_ordered(grid, reverse=False):
    padded_grid = add_grid_padding(grid)
    show(padded_grid)

    start, end = find_path_ends(padded_grid)
    if reverse:
        start, end = end, start

    pos = start
    visited = set([start])
    valid_moves = {"|", "-", "+", "X"}
    direction = "any"

    while pos and pos != end:
        nearby = neighbours(padded_grid, pos, skip=visited)

        if len(nearby) != 1:
            return False

        # try all moves:
        # for move, next_pos in nearby:
        move, next_pos = nearby.pop()

        if move not in valid_moves:
            return False

        visited.add(next_pos)

        if direction == "horizontal" and next_pos[0] != pos[0]:
            return False
        elif direction == "vertical" and next_pos[1] != pos[1]:
            return False

        pos = next_pos

        if move == "-":
            valid_moves = {"X", "+", "-"}
            direction = "horizontal"
        elif move == "|":
            valid_moves = {"X", "+", "|"}
            direction = "vertical"
        elif move == "+":
            if direction == "horizontal":
                direction = "vertical"
                valid_moves = {"X", "+", "|"}
            else:
                direction = "horizontal"
                valid_moves = {"X", "+", "-"}

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

    grid = ["           ",
            "X---------X",
            "           ",
            "           "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["     ",
            "  X  ",
            "  |  ",
            "  |  ",
            "  X  "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["                    ",
            "     +--------+     ",
            "  X--+        +--+  ",
            "                 |  ",
            "                 X  ",
            "                    "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["                     ",
            "    +-------------+  ",
            "    |             |  ",
            " X--+      X------+  ",
            "                     "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["                      ",
            "   +-------+          ",
            "   |      +++---+     ",
            "X--+      +-+   X     "]
    expected = True
    show(grid, expected)
    assert has_valid_line(grid) == expected


    grid = ["   |--------+    ",
            "X---        ---+ ",
            "               | ",
            "               X "]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["              ",
            "   +------    ",
            "   |          ",
            "X--+      X   ",
            "              "]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = ["      +------+",
            "      |      |",
            "X-----+------+",
            "      |       ",
            "      X       "]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected

    grid = [" X  ",
            " |  ",
            " +  ",
            " X  "]
    expected = False
    show(grid, expected)
    assert has_valid_line(grid) == expected
