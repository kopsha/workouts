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


class SudokuPuzzle:
    SIZE = 9

    @classmethod
    def from_puzzle(cls, puzzle):
        new = cls()
        new.board = {
            (i, j): value
            for i, row in enumerate(puzzle)
            for j, value in enumerate(row)
            if value
        }
        new.update_moves()
        return new

    def __init__(self):
        self.board = dict()
        self.moves = list()

    def available_moves(self):

        def filter_moves(moves, value):
            return list(filter(lambda x: value , moves))

        for pos, options in self.moves:
            for value in options:
                # print("-->", pos, value)
                puzzle = SudokuPuzzle()
                puzzle.board = deepcopy(self.board)
                puzzle.board[pos] = value
                puzzle.update_moves()

                yield puzzle

    def is_solved(self):
        return len(self.board) == 81

    def update_moves(self):
        self.moves = list()
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                pos = i, j
                if pos not in self.board:
                    moves = self.valid_moves_of(pos)
                    if moves:
                        self.moves.append((pos, moves))

    def valid_moves_of(self, pos):
        """Given a grid and a position, compute all valid options"""
        if pos in self.board:
            return set()

        options = set(range(1, 10))

        # check by row
        row, col = pos
        options -= set(self.board[row, i] for i in range(self.SIZE) if (row, i) in self.board)
        # check by column
        options -= set(self.board[i, col] for i in range(self.SIZE) if (i, col) in self.board)
        # check by cell
        cell_row = row // 3
        cell_col = col // 3
        options -= set(
            self.board[cell_row * 3 + di, cell_col * 3 + dj]
            for di, dj in CELLS
            if (cell_row * 3 + di, cell_col * 3 + dj) in self.board
        )

        return options
    
    def __repr__(self) -> str:

        row_fmt = "|" + "|".join(["%s" * 3] * 3) + "|"
        row_sep = "+" + "+".join(["-" * 3] * 3) + "+"

        lines = list()
        for i in range(self.SIZE):
            if i % 3 == 0: lines.append(row_sep)

            lines.append(row_fmt % tuple(
                str(self.board.get((i, j), " ")) for j in range(self.SIZE)
            ))
        
        lines.append(row_sep)

        return "\n".join(lines)
    
    def as_board(self):
        return [
            (self.board.get((i, j, 0)) for j in range(self.SIZE))
            for i in range(self.SIZE) 
        ]


def solve(puzzle):
    """hopefully a faster version"""
    sudo_print(puzzle, "from")

    start = SudokuPuzzle.from_puzzle(puzzle)
    queue = deque([start])
    cnt = 0
    while queue:
        cnt += 1

        puzz = queue.popleft()

        if cnt % 1000 == 0:
            print("\t", cnt)
            print(puzz, flush=True)
        
        for m in puzz.available_moves():
            if m.is_solved():
                return m.as_board()
            
            queue.append(m)

    print(f"{start!r}")
    raise ValueError("Puzzle has no solutions.")

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
    actual = solve(puzzle)

    # sudo_print(actual)

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
