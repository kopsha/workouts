from itertools import permutations, chain
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


def sudo_print(puzzle, title=""):
    print(f"    {title}")
    for i, row in enumerate(puzzle):
        if i % 3 == 0:
            print("+---" * 3 + "+")
        augmented = [
            "|" * int(j % 3 == 0) + (str(x) if x else " ") for j, x in enumerate(row)
        ] + ["|",]
        print("".join(augmented))
    print("+---" * 3 + "+")


def sudoku_permutations(cell):
    """Generates all permutations given a starting position"""

    variable = set(SPACE) - set(cell)
    fixed = dict()
    var_pos = dict()

    for i, value in enumerate(cell):
        if value:
            fixed[i] = value
        else:
            var_pos[i] = len(var_pos)

    for x in permutations(variable):
        next_pos = [fixed[i] if i in fixed else x[var_pos[i]] for i in range(len(cell))]
        yield next_pos


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


def sudoku_generator(puzzle):
    """return the solved puzzle as a 2d array of 9 x 9"""

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
            yield puzzle
            puzzle[row][col] = 0


def is_solved(puzzle):
    return 0 not in set(chain.from_iterable(puzzle))


def canonical(puzzle):
    return "".join(str(x) for x in chain.from_iterable(puzzle))


def sudoku(puzzle):

    step = 0
    work_puzzle = deepcopy(puzzle)
    queue = deque([work_puzzle])
    trail = set([canonical(work_puzzle)])

    sudo_print(work_puzzle, title=f"{step=}")

    while not is_solved(work_puzzle):
        for m in sudoku_generator(work_puzzle):
            step += 1
            # print(f"--- {step=}")
            # pprint(m)
            # print(f"{trail=}")

            if step > 10:
                return work_puzzle
            if step % 1000 == 0:
                print(".", end="", flush=True)

            c = canonical(m)
            if c not in trail:
                trail.add(c)
                queue.appendleft(deepcopy(m))
        work_puzzle = queue.pop()

    return work_puzzle


def test_debug():
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

    assert False


def _test_basic_solver():
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
    pprint(actual)
    assert actual == expected
