#!/usr/bin/env python3
from itertools import cycle, count


MAX_LETTERS = 26


def as_num(char: str) -> int:
    assert len(char) == 1, f"Expected a single character, found {len(char)}"
    return ord(char.upper()) - ord("A")


def as_char(code: int) -> str:
    assert (code < MAX_LETTERS), f"Expected a code below {MAX_LETTERS}, found {code}"
    return chr(code + ord("A"))


def identify_progression(values: list) -> int | None:
    assert len(values) >= 2, f"Expected a longer list, found {len(values)} values."

    delta = values[1] - values[0]
    if all(right - left == delta for left, right in zip(values[:-1], values[1:])):
        return delta

    return None


class OTPCipher:
    def __init__(self, shared_secret: str) -> None:
        self.shared_secret = shared_secret

    @classmethod
    def from_message(cls, encrypted_message: str, known_secret: str):
        """Derive key from message and known secret"""

        xkey = list()
        for char, ki in zip(encrypted_message, known_secret):
            if char.isalpha():
                kx = (as_num(char) - as_num(ki)) % MAX_LETTERS
                xkey.append(kx)

        if delta := identify_progression(xkey) is not None:
            # extrapolate key if it's a simple arithmetic progression
            xgen = count(xkey[0], delta)
            xkey = (next(xgen) % MAX_LETTERS for _ in range(MAX_LETTERS))

        key = "".join(map(as_char, xkey))
        return cls(key)

    def encrypt(self, text: str) -> str:
        result = list()
        ki = cycle(self.shared_secret)
        for char in text:
            if char.isalpha():
                ec = (as_num(char) + as_num(next(ki))) % MAX_LETTERS
                result.append(as_char(ec))
            else:
                result.append(char)
        return "".join(result)

    def decrypt(self, encrypted: str) -> str:
        result = list()
        ki = cycle(self.shared_secret)
        for char in encrypted:
            if char.isalpha():
                ec = as_num(char)
                kc = as_num(next(ki))
                cc = (ec - kc) % MAX_LETTERS
                result.append(as_char(cc))
            else:
                result.append(char)
        return "".join(result)


def main():
    encrypted_message = "TGFVJZ FWDB ATBBT XRK UYZJ QYOPFF"
    known_secret = "SECRET"

    cipher = OTPCipher.from_message(encrypted_message, known_secret)
    decrypted = cipher.decrypt(encrypted_message)

    print(f"{encrypted_message=}")
    print(f"{decrypted=}")


if __name__ == "__main__":
    main()
