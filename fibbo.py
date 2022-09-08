import timeit


def fib(n):
    if n in {0, 1}:
        return n

    if n > 100_000:
        return fast_fib(n)

    a, b = 0, 1
    N = abs(n) - 1
    signum = 1 if n >= 0 else 1 - 2 * (N % 2)
    for _ in range(N):
        a, b = b, a + b

    return signum * b


def fast_fib(n):
    v1, v2, v3 = 1, 1, 0

    # perform fast exponentiation of the matrix (quickly raise it to the nth power)
    for rec in bin(n)[3:]:
        calc = v2 * v2
        v1, v2, v3 = v1 * v1 + calc, (v1 + v3) * v2, calc + v3 * v3
        if rec == "1":
            v1, v2, v3 = v1 + v2, v1, v2

    return v2


if __name__ == "__main__":
    call = "print(fib(1_000_000))"
    duration = timeit.timeit(
        call, setup="from __main__ import (fib, fast_fib)", number=1
    )
    print("computing", "call", "took", f"{duration:.3f}", "seconds")
