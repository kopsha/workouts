from itertools import chain, product
from copy import deepcopy
from collections import defaultdict


ROWS = "ABCDEFGHI"
COLS = "123456789"
SPACE = list(range(1, 10))

ALL_COORDS = [r + c for r, c in product(ROWS, COLS)]
BY_ROW = [list(map("".join, product(r, COLS))) for r in ROWS]
BY_COLUMN = [list(map("".join, product(ROWS, c))) for c in COLS]
BY_CELL = [
    list(map("".join, product(rs, cs)))
    for rs, cs in product(("ABC", "DEF", "GHI"), ("123", "456", "789"))
]
ALL_UNITS = BY_ROW + BY_CELL + BY_COLUMN
PEERS_OF = {coord: [u for u in ALL_UNITS if coord in u] for coord in ALL_COORDS}


def pos_of(coords):
    return ord(coords[0]) - ord("A"), ord(coords[1]) - ord("0")


def coords_of(pos):
    return ROWS[pos[0]] + COLS[pos[1]]


def as_matrix(board):
    return [[board[ri + ci] for ci in COLS] for ri in ROWS]


depth = 0


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


class SudokuPuzzle:
    SIZE = 9
    SEEN = set()

    def __init__(self):
        self.board = dict()

    def __repr__(self) -> str:

        row_fmt = "|" + "|".join(["%s" * 3] * 3) + "|"
        row_sep = "+" + "+".join(["-" * 3] * 3) + "+"

        lines = list()
        for i in range(self.SIZE):
            if i % 3 == 0:
                lines.append(row_sep)

            lines.append(
                row_fmt
                % tuple(
                    str(self.board.get(coords_of((i, j)), " "))
                    for j in range(self.SIZE)
                )
            )

        lines.append(row_sep)

        return "\n".join(lines)

    def __str__(self) -> str:
        return "".join(
            chain.from_iterable(
                [str(self.board.get(ri + ci, 0)) for ci in COLS] for ri in ROWS
            )
        )

    def is_solved(self):
        return len(self.board) == 81

    def options_for(self, coord):
        if coord in self.board:
            return set()

        options = set(SPACE) - set(
            self.board[co]
            for co in chain.from_iterable(PEERS_OF[coord])
            if co in self.board
        )

        return options

    def moves(self):
        result = [
            (co, options) for co in ALL_COORDS if (options := self.options_for(co))
        ]

        result.sort(key=lambda pair: len(pair[1]))
        return result

    @classmethod
    def from_board(cls, board):
        new = cls()
        new.board = {
            coords_of((i, j)): value
            for i, row in enumerate(board)
            for j, value in enumerate(row)
            if value
        }
        return new

    def alternate_print(self):
        alternate = defaultdict(list)
        for co, val in self.board.items():
            alternate[val].append(co)

        for val in sorted(alternate):
            print(f"{val}: {','.join(sorted(alternate[val]))}")

    def alternate_eval(self):
        alternate = defaultdict(list)
        for co, val in self.board.items():
            alternate[val].append(co)

        for val in range(1, 10):
            rowset = set(ROWS)
            colset = set(COLS)
            for co in alternate[val]:
                rowset.discard(co[0])
                colset.discard(co[1])
            print(val, "->", ",".join(sorted(alternate[val])))
            print("\t", ",".join(sorted(rowset)))
            print("\t", ",".join(sorted(colset)))

    def deep_solve(self):
        if self.is_solved():
            self.alternate_print()
            return deepcopy(self.board)

        global depth
        depth += 1
        this_depth = int(depth)
        SudokuPuzzle.SEEN.add(str(self))
        print(repr(self))
        # input(f"{depth=}")

        available_moves = self.moves()
        if not available_moves:
            print("[x] no valid moves")

        for co, options in available_moves:
            for value in options:
                self.board[co] = value
                print(f"\t{co} <- {value}")
                if str(self) in SudokuPuzzle.SEEN:
                    continue

                if solution := self.deep_solve():
                    return solution

            del self.board[co]
            depth = this_depth
            print(f"restoring {this_depth=} @ {co}")
            print(repr(self))

        return None


def solve(board):
    """hopefully a faster version"""
    start = SudokuPuzzle.from_board(board)
    print(repr(start))
    start.alternate_eval()
    input("check this out")
    # print("**********", len(start.board), 81 - len(start.board))
    solution = start.deep_solve()
    if solution:
        sudo_print(as_matrix(solution))
        return as_matrix(solution)

    raise ValueError("Puzzle has no solutions.")


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
    actual = solve(puzzle)

    # sudo_print(actual)

    assert False


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


def test_optimized_solver():
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


if __name__ == "__main__":
    test_basic_solver()
    # test_optimized_solver()
