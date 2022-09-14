'''
[11:05 AM] Volodymyr Truba
    # Create a Tic-Tac-Toe evaluator. Your solution should accept a list of lists of chars and the player's
# char, and return True if they have three in a row and false otherwise. For instance, the following grid
"""
x o _
o x _
_ o x
"""
# would be called as below:
my_grid = [['x', 'o', '_'],
['o', 'x', '_'],
['_', 'o', 'x']]
print(won_tic_tac_toe(my_grid, 'x'))
# the evaluator would return True. If the grid instead looked like this:
"""
x o _
_ x _
_ o o
"""
# The evaluator would return False.
'''


def won_tic_tac_toe(grid, player):
    size = len(grid)
    # assert size == len(grid[0])

    # check horizontal lines
    for row in range(size):
        if all(grid[row][column] == player for column in range(size)):
            return True

    # check vertical lines
    for column in range(size):
        if all(grid[row][column] == player for row in range(size)):
            return True

    # check diagonals
    if all(grid[i][i] == player for i in range(size)):
        return True

    return False


def test_horizontal():
    my_grid = [
        ["x", "x", "x"],
        ["o", "x", "o"],
        ["_", "o", "_"],
    ]
    assert won_tic_tac_toe(my_grid, "x") == True


def test_vertical():
    my_grid = [
        ["x", "o", "x"],
        ["x", "o", "o"],
        ["_", "o", "_"],
    ]
    assert won_tic_tac_toe(my_grid, "o") == True


def test_diagonal():
    my_grid = [
        ["x", "o", "_"],
        ["o", "x", "_"],
        ["_", "o", "x"],
    ]
    assert won_tic_tac_toe(my_grid, "x") == True
