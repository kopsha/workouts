def is_valid_walk(walk):
    steps = dict()
    pass


def test_walk():
    test_values = (
        (["w", "False"]),
        (["n", "s", "n", "s", "n", "s", "n", "s", "n", "s"], True),
        (["w", "e", "w", "e", "w", "e", "w", "e", "w", "e", "w", "e"], False),
        (["n", "n", "n", "s", "n", "s", "n", "s", "n", "s"], False),
    )

    for path, expected in test_values.items():
        actual = is_valid_walk(path)
        ppath = "".join(path)
        assert (
            actual == expected
        ), f"For input {ppath}, expecting {expected}, got {actual} instead."
