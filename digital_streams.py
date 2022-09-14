def make_digital_stream(start, length):
    count = start
    parts = str()

    while len(parts) < length:
        parts += str(count)
        count += 1

    return parts[:length]


def first_position(of: str):
    n = int(of)

    pos = 0
    if len(of) <= 1:
        pos = n - 1
    elif len(of) <= 2:
        pos = 9 + (n - 10) * 2
    elif len(of) <= 3:
        pos += (n - 100) * 3

    print(f"{of=}, {pos=}")
    return pos


def find_position(number_stream):
    print(f"{number_stream=}, {len(number_stream)=}")
    length = len(number_stream)
    if length < 1:
        return 0
    elif length == 1:
        return first_position(number_stream)

    # find partial consecutives
    for digits in range(1, length + 1):
        start = int(number_stream[:digits])
        lucky = make_digital_stream(start, length)
        print(digits, start, lucky)
        if lucky == number_stream:
            return first_position(str(number_stream[:digits]))

    return 0


def test_streams():
    test_values = {
        "1": 0,
        "2": 1,
        "9": 8,
        "91": 8,
        "10": 9,
        "910": 8,
        "456": 3,
        "454": 79,
        "455": 98,
        "9100": 188,
        "99100": 187,
        "00101": 190,
        "001": 190,
        "00": 190,
        "123456789": 0,
        "1234567891": 0,
        "123456798": 1000000071,
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
        print(word, expected, "passed")
