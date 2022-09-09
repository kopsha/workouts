from math import factorial
from functools import reduce
from collections import Counter


def count_permutations(of: str):
    counters = {letter: of.count(letter) for letter in of}
    result = factorial(sum(counters.values()))
    for count in counters.values():
        result //= factorial(count)
    return result


def lexicographical_index(word):
    rank, length, freqs = 0, len(word), Counter(word)
    for i, letter in enumerate(word):
        fsum = sum(freqs[c] for c in set(word) if c < letter)
        fprod = reduce(lambda x, y: y * x, (factorial(v) for v in freqs.values()))
        freqs[letter] -= 1
        rank += (fsum * factorial(length - i - 1)) // fprod

    return rank + 1


def test_anagram():
    test_values = {
        "A": 1,
        "AAAB": 1,
        "ABAB": 2,
        "TIMEX": 81,
        "BAAB": 4,
        "BAAA": 4,
        "BBTA": 7,
        "QUESTION": 24572,
        "BOOKKEEPER": 10743,
    }
    for word, expected in test_values.items():
        actual = lexicographical_index(word)
        assert (
            actual == expected
        ), f"For input {word}, expecting {expected}, got {actual} instead."
