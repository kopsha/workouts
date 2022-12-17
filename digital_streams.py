def generate_stream_options(start_options, number_stream):
    """
    Attempts each start value and returns only the ones that matches the desired
    stream and its offset
    """
    options = list()
    length = len(number_stream)
    for start in start_options:
        count = start
        parts = str()
        while len(parts) <= (length * 3):
            parts += str(count)
            count += 1

        if number_stream in parts:
            options.append((start, parts.find(number_stream)))

    return options


def index_of(start: int):
    """finds the index of any given start value"""
    if start < 10:
        return start - 1

    digits = str(start)

    # count space for all numbers with less than size digits
    pos = 0
    for i in range(len(digits) - 1):
        multi = 9 * 10**i
        this = (i + 1) * multi
        pos += this

    i += 1
    multi = start - 10**i
    this = (i + 1) * multi
    pos += this

    # count space for numbers with size digits
    return pos


def find_position(number_stream):
    """
    Trying all consecutive parts, starting with the lowest number of digits
    """
    solutions = list()
    length = len(number_stream)

    for window in range(1, length + 1):
        for offset in range(length):
            partial = str(number_stream[offset : offset + window])
            missing = window + offset - length
            start_options = set()

            if missing > 0:
                missing_part = str(number_stream[offset - missing : offset])
                if missing_part.endswith("9"):
                    alt_partial = str(int(partial + "0" * missing) - 1)
                    start_options.add(int(alt_partial))

                partial += missing_part

            start = int(partial)
            start_options.add(int(partial))
            start_options.add(start - 1)
            start_options.add(start)

            if partial.startswith("0"):
                start_options.add(10 ** len(partial))
                start += 10 ** len(partial)

            start_options = {max(x, 1) for x in start_options}

            luckies = generate_stream_options(start_options, number_stream)
            for lucky_start, offi in luckies:
                solutions.append(index_of(lucky_start) + offi)

    return min(solutions)


def test_streams():
    test_values = {
        "456": 3,
        "454": 79,
        "1": 0,
        "2": 1,
        "9": 8,
        "91": 8,
        "92": 28,
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
