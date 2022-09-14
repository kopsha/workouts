def is_valid_walk(walk):

    if len(walk) != 10:
        return False

    x, y = 0, 0
    deltas = dict(
        e=(-1, 0),
        w=(+1, 0),
        n=(0, -1),
        s=(0, +1),
    )

    for step in walk:
        dx, dy = deltas[step]
        x, y = x + dx, y + dy

    return (x, y) == (0, 0)


def test_walk():
    test_values = (
        (["w"], False),
        (["n", "s", "n", "s", "n", "s", "n", "s", "n", "s"], True),
        (["w", "e", "w", "e", "w", "e", "w", "e", "w", "e", "w", "e"], False),
        (["n", "n", "n", "s", "n", "s", "n", "s", "n", "s"], False),
    )

    for path, expected in test_values:
        actual = is_valid_walk(path)
        ppath = "".join(path)
        assert (
            actual == expected
        ), f"For input {ppath}, expecting {expected}, got {actual} instead."
