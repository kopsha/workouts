def is_valid_walk(walk):
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

    print("".join(walk), x, y)

    return (x, y) == (0, 0)


if __name__ == "__main__":
    test.expect(
        is_valid_walk(["n", "s", "n", "s", "n", "s", "n", "s", "n", "s"]),
        "should return True",
    )
    test.expect(
        not is_valid_walk(["w", "e", "w", "e", "w", "e", "w", "e", "w", "e", "w", "e"]),
        "should return False",
    )
    test.expect(not is_valid_walk(["w"]), "should return False")
    test.expect(
        not is_valid_walk(["n", "n", "n", "s", "n", "s", "n", "s", "n", "s"]),
        "should return False",
    )
