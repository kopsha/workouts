
def make_digital_stream(length):

    count = 0
    parts = list()

    while count < length:
        count += 1
        parts.append(str(count))

    return "".join(parts)


def find_position(word):
    length = len(word)
    if length < 1:
        return 0
    elif length == 1:
        return ord(word) - ord("0")

    print(f"Got {word=}")
    deltas = [ord(right)-ord(left) for left, right in zip(word[:-1], word[1:])]
    print(f"{deltas=}")

    return 0


def test_stream_gen():
    for i in (25, 1000):
        stream = make_digital_stream(i)
        print(f"{i=}, {stream=}")

        prev = None
        for j, c in enumerate(stream):
            if c == "9":
                print(j, j-prev if prev else "")
                prev = j
    assert False


def dont_test_streams():
    test_values = {
        "456": 3,
        "454": 79,
        "455": 98,
        "910": 8,
        "9100": 188,
        "99100": 187,
        "00101": 190,
        "001": 190,
        "00": 190,
        "123456789": 0,
        "1234567891": 0,
        "123456798": 1000000071,
        "10": 9,
        "53635": 13034,
        "040": 1091,
        "11": 11,
        "99": 168,
        "667": 122,
        "0404": 15050,
        "949225100": 382689688,
        "58257860625": 24674951477,
        "3999589058124": 6957586376885,
        "555899959741198": 1686722738828503,
        "01": 10,
        "091": 170,
        "0910": 2927,
        "0991": 2617,
        "09910": 2617,
        "09991": 35286,
    }
    for word, expected in test_values.items():
        actual = find_position(word)
        assert (
            actual == expected
        ), f"For input {word}, expecting {expected}, got {actual} instead."
