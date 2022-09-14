def make_stream_options(start, length, offset):
    count = start
    parts = str()

    while len(parts) < (length + offset):
        parts += str(count)
        count += 1

    delta_offi = len(parts) - length + 1
    options = [(str(parts[offi:offi+length]), offi) for offi in range(delta_offi)]
    return options


def index_of(number: int):
    if number < 10:
        return number-1

    digits = str(number)

    # count space for all numbers with less than size digits
    pos = 0
    for i in range(len(digits) - 1):
        multi = 9 * 10 ** i
        this = (i + 1) * multi
        pos += this
        print(f"\t {i=}, {multi=}, {this=}")

    i += 1
    multi = number - 10 ** i
    this = (i + 1) * multi
    pos += this

    # count space for numbers with size digits
    return pos


def find_position(number_stream):
    print(f"{number_stream=}, {len(number_stream)=}")
    length = len(number_stream)
    if length < 1:
        return 0

    # find partial consecutives
    for window in range(1, length + 1):
        for offset in range(window):
            partial = number_stream[offset:offset+window]
            start = int(partial)

            if partial.startswith("0"):
                start += 10 ** len(partial)

            lucky = make_stream_options(start, length, offset)
            print(f"{window=} {offset=}, {partial=}, {start=}, {lucky=}")
            for lucky_stream, offi in lucky:
                if number_stream == lucky_stream:
                    return index_of(start) + offi

            start -= 1
            lucky = make_stream_options(start, length, offset)
            print(f"{window=} {offset=}, {partial=}, {start=}, {lucky=}")
            for lucky_stream, offi in lucky:
                if number_stream == lucky_stream:
                    return index_of(start) + offi

    return 0


def test_streams():
    test_values = {
        "456": 3,
        "454": 79,
        "1": 0,
        "2": 1,
        "9": 8,
        "91": 8,
        "10": 9,
        "910": 8,
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
