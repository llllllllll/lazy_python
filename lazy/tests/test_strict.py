from lazy import strict, thunk


def test_strict_prim():
    assert strict(5) is 5


def test_strict_thunk():
    assert strict(thunk.fromexpr(5)) is 5
    assert strict(thunk(lambda a: a, 5)) is 5


def test_strict_method():
    class C:
        def __strict__(self):
            return 5

    assert strict(C()) is 5
    assert strict(C) is C
