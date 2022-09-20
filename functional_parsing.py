
class RegExp:
    def __init__(self, *args):
        self.args = args
    def __repr__(self):
        args = ", ".join(map(repr, self.args))
        return f"{self.__class__.__name__}({args})"
    def __eq__(self, other):
        return type(self) is type(other) and self.args == other.args
class Any(RegExp): pass
class Normal(RegExp): pass
class Or(RegExp): pass
class Str(RegExp): pass
class ZeroOrMore(RegExp): pass


def parse_regexp(indata):
    print("-", indata, type(indata))
    return Any()



def check(indata, expected):
    actual = parse_regexp(indata)
    assert actual == expected, f"Given {indata!r} expecting {expected!r} but got {actual!r} instead."


def test_basic_expressions():
    check(".", Any())
    check("a", Normal("a"))
    check("a|b", Or(Normal("a"), Normal("b")))
    check("a*", ZeroOrMore(Normal("a")))
    check("(a)", Normal("a"))
    check("(a)*", ZeroOrMore(Normal("a")))
    check("(a|b)*", ZeroOrMore(Or(Normal("a"), Normal("b"))))
    check("a|b*", Or(Normal("a"), ZeroOrMore(Normal("b"))))
    check("abcd", Str([Normal("a"), Normal("b"), Normal("c"), Normal("d")]))
    check("ab|cd", Or(Str([Normal("a"), Normal("b")]), Str([Normal("c"), Normal("d")])))


def test_precedence():
    check("ab*", Str([Normal("a"), ZeroOrMore(Normal("b"))]))
    check("(ab)*", ZeroOrMore(Str([Normal("a"), Normal("b")])))
    check("ab|a", Or(Str([Normal("a"), Normal("b")]), Normal("a")))
    check("a(b|a)", Str([Normal("a"), Or(Normal("b"), Normal("a"))]))
    check("a|b*", Or(Normal("a"), ZeroOrMore(Normal("b"))))
    check("(a|b)*", ZeroOrMore(Or(Normal("a"), Normal("b"))))


def test_other_examples()
    check("a", Normal("a"))
    check("ab", Str([Normal("a"), Normal("b")]))
    check("a.*", Str([Normal("a"), ZeroOrMore(Any())]))
    check("(a.*)|(bb)", Or(Str([Normal("a"), ZeroOrMore(Any())]), Str([Normal("b"), Normal("b")])))


def test_invalid_examples():
    check("", None)
    check("(", None)
    check("(hi!", None)
    check(")(", None)
    check("a|t|y", None)
    check("a**", None)


def test_complex_examples():
    check("((aa)|ab)*|a", Or(ZeroOrMore(Or(Str([Normal("a"), Normal("a")]), Str([Normal("a"), Normal("b")]))), Normal("a")))
    check("((a.)|.b)*|a", Or(ZeroOrMore(Or(Str([Normal("a"), Any()]), Str([Any(), Normal("b")]))), Normal("a")))
