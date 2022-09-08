from math import factorial
from itertools import permutations


def anagram_position(word):
    """Return the anagram list position of the word"""
    N = len(word)
    letters = list(sorted(set(word)))
    counters = {l: word.count(l) for l in letters}

    K = factorial(N)
    for c in counters.values():
        K //= factorial(c)

    M = sum(counters.values())
    multi = {l: c * K // M for l,c in counters.items()}

    print(word, K, counters)
    print(multi)

    for pp in sorted(set(permutations(word))):
        xx = "".join(str(letters.index(x)) for x in pp)
        ppp = "".join(pp)
        print(xx, ppp)

    return K


def test_anagram():
    test_values = {'A' : 1, 'ABAB' : 2, 'AAAB' : 1, 'BAAA' : 4, "BBTA": 10, 'QUESTION' : 24572, 'BOOKKEEPER' : 10743}
    for word, expected in test_values.items():
        actual = anagram_position(word)
        assert actual == expected, f"For input {word}, expecting {expected}, got {actual} instead."
