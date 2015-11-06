import sys

import pytest

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


@pytest.mark.parametrize('f,val', (
    (lambda: 1, 1),
    (lambda: 'a', 'a'),
    (lambda: (1, 2), (1, 2)),
    (lambda: b'a', b'a'),
))
def test_const(f, val):
    f = strict(lazy_function(f))

    assert isinstance(f(), thunk)
    assert f() == val


def test_dict_literal():
    @strict
    @lazy_function
    def f():
        return {'a': 1, 'b': 2}

    assert isinstance(f(), thunk)
    assert f() == {'a': 1, 'b': 2}
    assert isinstance(f()['a'], thunk)


def test_dict_comprehension():
    @strict
    @lazy_function
    def f():
        return {n: n for n in range(2)}

    assert isinstance(f(), thunk)
    assert f() == {0: 0, 1: 1}
    assert isinstance(f()[0], thunk)


def test_set_literal():
    @strict
    @lazy_function
    def f():
        return {'a', 'b'}

    assert isinstance(f(), thunk)
    assert f() == {'a', 'b'}
    assert isinstance(tuple(f())[0], thunk)


def test_set_comprehension():
    @strict
    @lazy_function
    def f():
        return {c for c in 'ab'}

    assert isinstance(f(), thunk)
    assert f() == {'a', 'b'}
    assert isinstance(tuple(f())[0], thunk)


def test_list_literal():
    @strict
    @lazy_function
    def f():
        return ['a', 'b']

    assert isinstance(f(), thunk)
    assert f() == ['a', 'b']
    assert isinstance(f()[0], thunk)


def test_list_comprehension():
    @strict
    @lazy_function
    def f():
        return [c for c in 'ab']

    assert isinstance(f(), thunk)
    assert f() == ['a', 'b']
    assert isinstance(f()[0], thunk)


def test_import_name():
    sys.modules.pop('__hello__', None)

    @strict
    @lazy_function
    def f():
        import __hello__
        return __hello__

    hello_module_thunk = f()
    assert '__hello__' not in sys.modules
    hello_module = strict(hello_module_thunk)
    assert hello_module.__name__ == '__hello__'
    assert '__hello__' in sys.modules


def test_import_from():
    sys.modules.pop('__hello__', None)

    @strict
    @lazy_function
    def f():
        from __hello__ import initialized
        return initialized

    initialized_thunk = f()
    assert '__hello__' not in sys.modules
    assert initialized_thunk
    assert '__hello__' in sys.modules
