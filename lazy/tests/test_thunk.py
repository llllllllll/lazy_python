from itertools import starmap
import math
import operator

import pytest

from lazy import thunk, strict


no_implicit_thunk = object()
reflect_implicit = object()
magic_class = object()


def prep_magic_func_args(func, args):
    try:
        first_arg = args[0]
    except IndexError:
        first_arg = None

    if first_arg is no_implicit_thunk:
        args = args[1:]
    elif first_arg is reflect_implicit:
        args = args[1:] + (thunk(object),)
    elif first_arg is magic_class:
        args = (class_factory(func)(),)
    else:
        args = (thunk(object),) + args[1:]

    return func, args


def class_factory(func):
    """
    Constructs a type with a given magic that will raise an exception
    when called.

    For example:

    >>> class_factory(operator.add)
    <class 'add_test_class'>

    This is a class which will raise a type error with the message '__add__'
    when you try to use the addition operator on instances.
    """
    magic = '__%s__' % func.__name__

    def raiser(self):
        raise TypeError(magic)

    return type('%s_test_class' % magic, (object,), {magic: raiser})


def call(f, *args, **kwargs):
    """
    Alias to make the metaclass magic defer to __call__.
    """
    return f(*args, **kwargs)


@pytest.mark.parametrize('f,args', starmap(prep_magic_func_args, (
    (operator.eq, (thunk(object),)),
    (operator.ne, (thunk(object),)),
    (operator.lt, (thunk(object),)),
    (operator.gt, (thunk(object),)),
    (operator.le, (thunk(object),)),
    (operator.ge, (thunk(object),)),
    (operator.pos, ()),
    (operator.neg, ()),
    (abs, ()),
    (operator.invert, ()),
    (round, ()),
    (math.floor, ()),
    (math.ceil, ()),
    (math.trunc, (magic_class,)),
    (operator.add, (int(),)),
    (operator.add, (reflect_implicit, int())),
    (operator.iadd, ()),
    (operator.sub, (int(),)),
    (operator.sub, (reflect_implicit, int())),
    (operator.isub, ()),
    (operator.mul, (int(),)),
    (operator.mul, (reflect_implicit, int())),
    (operator.imul, ()),
    (operator.floordiv, (int(),)),
    (operator.floordiv, (reflect_implicit, int())),
    (operator.ifloordiv, (int(),)),
    (operator.truediv, (int(),)),
    (operator.truediv, (reflect_implicit, int())),
    (operator.itruediv, (int(),)),
    (operator.mod, (int(),)),
    (operator.mod, (reflect_implicit, int())),
    (operator.imod, (int(),)),
    (divmod, (int(),)),
    (divmod, (reflect_implicit, int())),
    (pow, (int(),)),
    (pow, (reflect_implicit, int()),),
    (operator.ipow, ()),
    (operator.lshift, (int(),)),
    (operator.lshift, (reflect_implicit, int())),
    (operator.ilshift, ()),
    (operator.rshift, (int(),)),
    (operator.rshift, (reflect_implicit, int())),
    (operator.irshift, ()),
    (operator.and_, (int(),)),
    (operator.and_, (reflect_implicit, int())),
    (operator.iand, ()),
    (operator.or_, (int(),)),
    (operator.or_, (reflect_implicit, int())),
    (operator.ior, ()),
    (operator.xor, (int(),)),
    (operator.xor, (reflect_implicit, int())),
    (operator.ixor, (int(),)),
    (int, (magic_class,)),
    (float, (magic_class,)),
    (complex, (magic_class,)),
    (oct, (magic_class,)),
    (hex, (magic_class,)),
    (operator.index, (magic_class,)),
    (str, (magic_class,)),
    (bytes, (magic_class,)),
    (repr, (magic_class,)),
    (hash, (magic_class,)),
    (bool, (magic_class,)),
    (dir, (magic_class,)),
    (len, (magic_class,)),
    (iter, (magic_class,)),
    (reversed, (magic_class,)),
    (call, (magic_class,)),
)))
def test_magic_func(f, args):
    """
    The actual test case for a the magic inner type.
    """
    a = thunk(f, *args)
    with pytest.raises(TypeError):
        strict(a)


def test_laziness():
    def raiser():
        raise ValueError('raiser raised')

    a = thunk(raiser)

    with pytest.raises(ValueError):
        strict(a)


def test_isinstance_strict():
    th = thunk(lambda: 2)
    assert isinstance(th, int)
    assert isinstance(th, thunk)


def test_iter():
    """
    Tests that lazy iteration is correct and terminates.
    This is a strict point.
    """
    t = thunk(lambda: (1, 2, 3))
    it = iter(t)

    assert isinstance(it, thunk)

    def isthunk(a):
        assert isinstance(a, thunk)
        return a

    vals = tuple(map(isthunk, it))
    assert vals == t

    with pytest.raises(StopIteration):
        next(it)


class Sub(thunk):
    pass


@pytest.mark.parametrize('type_', (thunk, Sub))
def test_fromexpr_of_thunk(type_):
    a = thunk.fromexpr(type_.fromexpr(1))
    assert isinstance(a, type_)
    assert isinstance(strict(a), int)
    assert not isinstance(strict(a), type_)


@pytest.fixture
def s():
    return Sub.fromexpr(1)


def test_subclass(s):
    """
    Tests the basics.
    """
    # Assert the basics
    assert isinstance(s, Sub)
    assert isinstance(s, thunk)
    assert isinstance(s, int)
    assert s == 1


def test_subclass_getattr(s):
    assert isinstance(s.getattr_check, Sub), 'tp_getattro did not return a Sub'


def test_subclass_call(s):
    assert isinstance(s(1), Sub), 'tp_call did not return a Sub'


def test_subclass_binop(s):
    assert isinstance(s + 1, Sub), 'THUNK_BINOP did not return a Sub'


def test_subclass_power(s):
    assert isinstance(s ** 1, Sub), 'thunk_power did not return a Sub'


def test_subblass_iter(s):
    assert isinstance(iter(s), Sub), 'thunk_iter did not return a Sub'


def test_subclass_next():
    n = next(Sub(lambda: iter((1, 2, 3))))
    assert isinstance(n, Sub), 'thunk_next did not return a Sub'


def test_subclass_richcmp(s):
    assert isinstance(s > 0, Sub), 'thunk_richcmp did not return a Sub'
