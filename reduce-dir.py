def reduce_direction(steps):
    opposites = {
        ("EAST", "WEST"),
        ("WEST", "EAST"),
        ("NORTH", "SOUTH"),
        ("SOUTH", "NORTH"),
    }
    reduced_steps = list()

    for step in steps:
        pair = reduced_steps[-1] if reduced_steps else None, step
        if pair in opposites:
            reduced_steps.pop()
        else:
            reduced_steps.append(step)

    return reduced_steps


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
