from lazy import thunk, strict, lazy_function


@strict
@lazy_function
def f(a, b):
    return a + b


def test_is_lazy():
    assert isinstance(f(1, 2), thunk)


def test_not_decorator():
    def g(a, b):
        return a - b

    g = lazy_function(g)
    assert isinstance(g(1, 2), thunk)


def test_lazy_call():
    called = False

    @lazy_function
    def g():
        nonlocal called
        called = True

    result = g()
    assert not called

    strict(result)
    assert called


def test_is():
    @lazy_function
    def g():
        return 1 is 1

    a = g()
    assert isinstance(a, thunk)
    assert strict(a)

    @lazy_function
    def h(a):
        return a is None

    b = h(None)
    assert isinstance(b, thunk)
    assert strict(b)

    c = h('not none')
    assert isinstance(c, thunk)
    assert not strict(c)


def test_not():
    @lazy_function
    def g():
        return not 1

    a = g()
    assert isinstance(a, thunk)
    assert not strict(a)

    @lazy_function
    def h(a):
        return not a

    b = h(False)
    assert isinstance(b, thunk)
    assert strict(b)

    c = h(True)
    assert isinstance(c, thunk)
    assert not strict(c)
