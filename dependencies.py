from collections import deque


def compute_deps(pkg_deps):
    """kahn's algorithm"""

    ordered_packages = list()
    edges = set()

    in_degree = {node: 0 for node in pkg_deps}
    for pkg, deps in pkg_deps.items():
        for dep in deps:
            in_degree[dep] += 1
            edges.add((pkg, dep))

    deepest = [pkg for pkg, count in in_degree.items() if count == 0]
    queue = deque(deepest)

    while queue:
        node = queue.popleft()
        ordered_packages.append(node)

        for pkg, dep in list(filter(lambda x: x[0] == node, edges)):
            edges.remove((pkg, dep))
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if edges:
        raise ValueError("Expected a graph without cycles")

    ordered_packages.reverse()
    return ordered_packages


def main():

    sample1 = dict(
        A=[],
        B=["A"],
        C=["D", "E"],
        D=[],
        E=["B"],
    )
    actual = compute_deps(sample1)
    print(sample1, "=>", actual)
    assert any(
        (
            ["A", "B", "D", "E", "C"] == actual,
            ["A", "B", "E", "D", "C"] == actual,
        )
    ), "basic example"

    sample2 = {
        "A": [],
        "B": ["A"],
        "C": ["B"],
        "D": ["C"],
    }
    actual = compute_deps(sample2)
    print(sample2, "=>", actual)
    assert actual == ["A", "B", "C", "D"], "easy example"

    sample3 = {
        "A": [],
        "B": [],
        "C": ["D"],
        "D": ["B"],
        "E": ["A", "B"],
        "F": ["A", "C"],
    }
    actual = compute_deps(sample3)
    print(sample3, "=>", actual)
    assert any(
        (
            ["B", "D", "C", "A", "F", "E"] == actual,
            ["B", "D", "A", "C", "F", "E"] == actual,
        )
    ), "geeks example"


if __name__ == "__main__":
    main()
