from math import factorial
from collections import deque
from itertools import permutations
import string


ADIGITS = string.digits + string.ascii_uppercase


def int2base(x, base):
    """Convert to any base smaller than the no of letters in english alphabet"""

    if x == 0:
        return ADIGITS[0]
    elif x < 0:
        sign = -1
    else:
        sign = 1

    value = sign * x
    digits = list()

    while value:
        value, remainder = divmod(base)
        digits.append(ADIGITS[remainder])

    if sign < 0:
        digits.append("-")

    return "".join(reversed(digits))


def anagram_position(word):
    """Return the anagram list position of the word"""

    N = len(word)
    if N == 1:
        return 1

    letters = list(sorted(set(word)))
    counters = {l: word.count(l) for l in letters}

    total = factorial(N)
    for c in counters.values():
        total //= factorial(c)

    sequence_len = sum(counters.values())

    burndown = list()
    for pos, letter in enumerate(reversed(word)):
        i = N - pos
        www = word[i:]
        L = factorial(len(www)) if www else 0
        print(pos, www, L)
        for rl in set(www):
            L //= factorial(www.count(rl))
        burndown.append((letter, L))

    burndown.reverse()
    print(burndown)

    base = len(letters)


    for i, pp in enumerate(sorted(set(permutations(word)))):
        xx = "".join(ADIGITS[letters.index(x)] for x in pp)
        yy = int(xx, base=base)
        ppp = "".join(pp)
        print(f"{i=}, {xx=}, {yy=}, {ppp=}")


    print(f"{word=}, {counters=}, {base=}, {total=}, {sequence_len=}")

    steps = list()
    result = 0
    remaining = total
    for pos, letter in enumerate(word):

        remaining_word = word[pos+1:]
        remaining = factorial(N-pos-1)
        for rl in set(remaining_word):
            remaining //= factorial(remaining_word.count(rl))

        remaining_digits = "".join(sorted(set(word[pos:])))
        starts = remaining_digits.index(letter)

        result += starts * remaining
        steps.append(starts)
        print(f"{letter=}, {remaining_digits=}, {starts=}, {remaining_word=}, {remaining=}, {result=}, {steps=}")

    result += remaining

    return result


def test_anagram():
    test_values = {
        "A": 1,
        "TIMEX": 81,
        "BAAB": 4,
        "ABAB": 2,
        "AAAB": 1,
        "BAAA": 4,
        "BBTA": 8,
        "QUESTION": 24572,
        "BOOKKEEPER": 10743,
    }
    for word, expected in test_values.items():
        actual = anagram_position(word)
        assert (
            actual == expected
        ), f"For input {word}, expecting {expected}, got {actual} instead."
