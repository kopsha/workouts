from math import sqrt
from functools import cache, reduce


@cache
def factors(x: int):
    facts = list()
    q, r = divmod(x, 2)
    while r == 0:
        facts.append(2)
        x = q
        q, r = divmod(x, 2)

    di, largest = 3, int(sqrt(x)) + 1
    while di <= largest:
        q, r = divmod(x, di)
        while r == 0:
            facts.append(di)
            x = q
            largest = int(sqrt(x)) + 1
            q, r = divmod(x, di)
        di += 2

    if x > 1:
        facts.append(x)

    return facts


def gcd(x, y):
    while x != y:
        if x > y:
            x -= y
        else:
            y -= x
    return x


def gcd_multi(xs: list):
    return reduce(gcd, xs[1:], xs[0])


def lcm(x, y):
    m, n = x, y
    while m != n:
        if m < n:
            m += x
        else:
            n += y
    return m


def lcm_multi(xs: list):
    return reduce(lcm, xs[1:], xs[0])




for i in range(2, 160):
    print(i, factors(i))
