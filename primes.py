from math import sqrt
from functools import cache


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


for i in range(2, 160):
    print(i, factors(i))
