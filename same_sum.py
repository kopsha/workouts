from collections import defaultdict
from itertools import combinations


def find_pairs_with_equal_sum(numbers: list):
    collector = defaultdict(list)
    for pair in combinations(numbers, 2):
        collector[sum(pair)].append(pair)

    pairs_by_sum = {s: pairs for s, pairs in collector.items() if len(pairs) > 1}
    return pairs_by_sum


def test_find_pairs_with_equal_sum():
    given = []
    actual = find_pairs_with_equal_sum(given)
    assert bool(actual) is False, "Empty list must return empty dict"

    for i in range(4):
        given = list(range(i))
        actual = find_pairs_with_equal_sum(given)
        assert bool(actual) is False, "Cannot make pairs with less than four values"

    given = list(range(4))
    actual = find_pairs_with_equal_sum(given)
    assert len(actual) == 1, "The simplest range must have exactly one pair"
    assert actual == {3: [(0, 3), (1, 2)]}, "The simplest range value mismatch"

    given = list(range(5))
    actual = find_pairs_with_equal_sum(given)
    assert len(actual) == 3, "The five range must have exactly three pairs"
    assert actual == {
        3: [(0, 3), (1, 2)],
        4: [(0, 4), (1, 3)],
        5: [(1, 4), (2, 3)],
    }, "The five range value mismatch"
    print("all tests pass")


if __name__ == "__main__":
    test_find_pairs_with_equal_sum()

    sample_one = [6, 4, 12, 10, 22, 54, 32, 42, 21, 11]
    print("Scanning", sample_one, "...")
    pairs_by_sum = find_pairs_with_equal_sum(sample_one)

    for s in sorted(pairs_by_sum):
        print(" - pairs:", *pairs_by_sum[s], "have sum:", s)

    sample_two = [4, 23, 65, 67, 24, 12, 86]
    print("Scanning", sample_two, "...")
    pairs = find_pairs_with_equal_sum(sample_two)
    pairs_by_sum = find_pairs_with_equal_sum(sample_two)

    for s in sorted(pairs_by_sum):
        print(" - pairs:", *pairs_by_sum[s], "have sum:", s)
