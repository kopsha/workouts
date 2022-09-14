def reduce_direction_nah(arr):
    """This actually works better, but the testcases..."""
    steps = [cmd.lower() for cmd in arr]
    deltas = dict(
        east=(-1, 0),
        west=(+1, 0),
        north=(0, -1),
        south=(0, +1),
    )

    x, y = 0, 0
    for step in steps:
        dx, dy = deltas[step]
        x, y = x + dx, y + dy
        print("\t", x, y)

    result = list()

    result.extend(["EAST"] * x if x < 0 else ["WEST"] * x)
    result.extend(["NORTH"] * y if y < 0 else ["SOUTH"] * y)

    return result


def remove_opposites(steps):
    opposites = {
        ("EAST", "WEST"),
        ("WEST", "EAST"),
        ("NORTH", "SOUTH"),
        ("SOUTH", "NORTH"),
    }
    result = list()
    touched = False

    i, j = 0, 1
    while j < len(steps):
        pair = (steps[i], steps[j])
        if pair in opposites:
            i, j = i + 2, j + 2
            touched = True
        else:
            result.append(steps[i])
            i, j = i + 1, j + 1

    if i < len(steps):
        result.append(steps[i])

    return result, touched


def reduce_direction(arr):
    steps, try_again = remove_opposites(arr)
    while try_again:
        steps, try_again = remove_opposites(steps)

    return steps


def test_reduce_direction():
    test_values = (
        (["NORTH", "SOUTH", "SOUTH", "EAST", "WEST", "NORTH", "WEST"], ["WEST"]),
        (["NORTH", "WEST", "SOUTH", "EAST"], ["NORTH", "WEST", "SOUTH", "EAST"]),
    )

    for path, expected in test_values:
        actual = reduce_direction(path)
        assert (
            actual == expected
        ), f"For input {path}, expecting {expected}, got {actual} instead."
