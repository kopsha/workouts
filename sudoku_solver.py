from itertools import chain
from copy import deepcopy
from collections import deque


SPACE = list(range(10))
CELLS = (
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 0),
    (1, 1),
    (1, 2),
    (2, 0),
    (2, 1),
    (2, 2),
)


def is_solved(puzzle):
    return 0 not in set(chain.from_iterable(puzzle))


def sudo_print(puzzle, title=""):

    if not puzzle:
        return

    print(f"    {title}")

    row_fmt = "|" + "|".join(["%s" * 3] * 3) + "|"
    row_sep = "+" + "+".join(["-" * 3] * 3) + "+"

    for i, row in enumerate(puzzle):
        if i % 3 == 0:
            print(row_sep)
        print(row_fmt % tuple(str(x) if x else " " for x in row))
    print("+---" * 3 + "+")
    print("    ", "solved" * is_solved(puzzle))


def valid_moves_of(pos, puzzle):
    """Given a grid and a position, compute all valid options"""
    row, col = pos
    if puzzle[row][col]:
        return set()

    N = len(puzzle)
    options = set(range(1, 10))

    # check by row
    options -= set(puzzle[row][i] for i in range(N) if puzzle[row][i])
    # check by column
    options -= set(puzzle[i][col] for i in range(N) if puzzle[i][col])
    # check by cell
    cell_row = row // 3
    cell_col = col // 3
    options -= set(
        puzzle[cell_row * 3 + di][cell_col * 3 + dj]
        for di, dj in CELLS
        if puzzle[cell_row * 3 + di][cell_col * 3 + dj]
    )

    return options


def sudoku(puzzle):
    """recursive version"""
    if is_solved(puzzle):
        return puzzle

    possible_moves = list()
    for i, row in enumerate(puzzle):
        for j, value in enumerate(row):
            pos = i, j
            if value == 0:
                options = valid_moves_of(pos, puzzle)
                if options:
                    possible_moves.append((pos, options))

    possible_moves.sort(key=lambda pair: len(pair[1]))

    for (row, col), options in possible_moves:
        for opt in options:
            puzzle[row][col] = opt
            solution = sudoku(puzzle)
            if solution:
                return solution
            puzzle[row][col] = 0

    return None


def canonical(puzzle):
    return "".join(str(x) if x else " " for x in chain.from_iterable(puzzle))


def sudo_show(flatline):
    n = 3
    "Display grid from a string (values in row major order with blanks for unknowns)"
    fmt = "|".join(["%s" * n] * n)
    sep = "+".join(["-" * n] * n)
    for i in range(n):
        for j in range(n):
            offset = (i * n + j) * n**2
            print(fmt % tuple(flatline[offset : offset + n**2]))
        if i != n - 1:
            print(sep)


def generate_sudoku_positions(puzzle):
    possible_moves = list()
    for i, row in enumerate(puzzle):
        for j, value in enumerate(row):
            pos = i, j
            if value == 0:
                options = valid_moves_of(pos, puzzle)
                if options:
                    possible_moves.append((pos, options))

    possible_moves.sort(key=lambda pair: len(pair[1]))

    for (row, col), options in possible_moves:
        for opt in options:
            puzzle[row][col] = opt
            print("\t", opt, "@", (row, col))
            yield puzzle
            puzzle[row][col] = 0


def solve(puzzle):
    """hopefully a faster version"""
    queue = deque([puzzle])
    cnt = 0
    while not is_solved(puzzle):
        sudo_print(puzzle, f"{cnt} {len(queue)=}")
        cnt += 1
        if cnt > 10:
            print("abort")
            return None

        for new_puzzle in generate_sudoku_positions(puzzle):
            queue.append(deepcopy(new_puzzle))
        puzzle = queue.pop()

    sudo_print(puzzle, "solution")
    return puzzle


def _test_debug():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    print("working...")
    actual = sudoku(puzzle)

    sudo_print(actual)

    assert False


def _test_recursive_solver():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    expected = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    actual = sudoku(puzzle)
    assert actual == expected


def test_basic_solver():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    expected = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    actual = solve(puzzle)
    assert actual == expected


def _test_optimized_solver():
    puzzle = [
        [9, 0, 0, 0, 8, 0, 0, 0, 1],
        [0, 0, 0, 4, 0, 6, 0, 0, 0],
        [0, 0, 5, 0, 7, 0, 3, 0, 0],
        [0, 6, 0, 0, 0, 0, 0, 4, 0],
        [4, 0, 1, 0, 6, 0, 5, 0, 8],
        [0, 9, 0, 0, 0, 0, 0, 2, 0],
        [0, 0, 7, 0, 3, 0, 2, 0, 0],
        [0, 0, 0, 7, 0, 5, 0, 0, 0],
        [1, 0, 0, 0, 4, 0, 0, 0, 7],
    ]

    expected = [
        [9, 2, 6, 5, 8, 3, 4, 7, 1],
        [7, 1, 3, 4, 2, 6, 9, 8, 5],
        [8, 4, 5, 9, 7, 1, 3, 6, 2],
        [3, 6, 2, 8, 5, 7, 1, 4, 9],
        [4, 7, 1, 2, 6, 9, 5, 3, 8],
        [5, 9, 8, 3, 1, 4, 7, 2, 6],
        [6, 5, 7, 1, 3, 8, 2, 9, 4],
        [2, 8, 4, 7, 9, 5, 6, 1, 3],
        [1, 3, 9, 6, 4, 2, 8, 5, 7],
    ]

    actual = solve(puzzle)
    assert actual == expected
