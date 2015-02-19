import math
import operator
from unittest import TestCase

from lazy import thunk, strict


no_implicit_thunk = object()
reflect_implicit = object()
magic_class = object()


class MagicTestDispatchMeta(type):
    def __new__(mcls, name, bases, dict_):
        for func, args in dict_.get('test_operators_lazy', ()):
            name = func.__name__

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

            full_name = 'test_%s_lazy' % name
            dict_[full_name] = _test_magic_func(func, full_name, args)

        return type.__new__(mcls, name, bases, dict_)


def _test_magic_func(f, name, args):
    def wrapper(self):
        a = thunk(f, *args)
        with self.assertRaises(TypeError):
            strict(a)

    wrapper.__name__ = name
    return wrapper


def class_factory(func):
    magic = '__%s__' % func.__name__

    def raiser(self):
        raise TypeError(magic)

    return type('%s_test_class' % magic, (object,), {magic: raiser})


def call(f, *args, **kwargs):
    """
    Alias to make the metaclass magic defer to __call__.
    """
    return f(*args, **kwargs)


def nonzero(a):
    """
    Alias to make the metaclass magic work under py2.
    """
    return bool(a)


class ThunkTestCase(TestCase, metaclass=MagicTestDispatchMeta):
    def test_laziness(self):
        def raiser():
            raise ValueError('raiser raised')

        a = thunk(raiser)

        with self.assertRaises(ValueError):
            strict(a)

    def test_isinstance_strict(self):
        th = thunk(lambda: 2)
        self.assertIsInstance(th, int)
        self.assertIsInstance(th, thunk)

    test_operators_lazy = (
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
    )
