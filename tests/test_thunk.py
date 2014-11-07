from functools import wraps
import math
import operator
from six import with_metaclass
from unittest import TestCase

from lazy.thunk import Thunk


no_implicit_thunk = object()
reflect_implicit = object()
magic_class = object()


class MagigTestDispatchMeta(type):
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
                args = args[1:] + (Thunk(object),)
            elif first_arg is magic_class:
                args = (class_factory(func)(),)
            else:
                args = (Thunk(object),) + args[1:]

            full_name = 'test_%s_lazy' % name
            dict_[full_name] = _test_magic_func(func, full_name, args)

        return type.__new__(mcls, name, bases, dict_)


def _test_magic_func(f, name, args):
    def wrapper(self):
        a = Thunk(object)
        a = Thunk(f, *args)
        with self.assertRaises(TypeError):
            a.strict

    wrapper.__name__ = name
    return wrapper


def class_factory(func):
    magic = '__%s__' % func.__name__

    def raiser(self):
        raise TypeError(magic)

    return type('%s_test_class' % magic, (object,), {magic: raiser})


def call(f, *args, **kwargs):
    return f(*args, **kwargs)


class ThunkTestCase(with_metaclass(MagigTestDispatchMeta, TestCase)):
    def test_laziness(self):
        def raiser():
            raise ValueError('raiser raised')

        a = Thunk(raiser)

        with self.assertRaises(ValueError):
            a.strict

    def test_isinstance_strict(self):
        thunk = Thunk(lambda: 2)
        self.assertIsInstance(thunk, int)
        self.assertIsInstance(thunk, Thunk)

    test_operators_lazy = (
        (operator.eq, (Thunk(object),)),
        (operator.ne, (Thunk(object),)),
        (operator.lt, (Thunk(object),)),
        (operator.gt, (Thunk(object),)),
        (operator.le, (Thunk(object),)),
        (operator.ge, (Thunk(object),)),
        (operator.pos, ()),
        (operator.neg, ()),
        (abs, ()),
        (operator.invert, ()),
        (round, ()),
        (math.floor, ()),
        (math.ceil, ()),
        (math.trunc, ()),
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

    def test_eq_value(self):
        a = Thunk(lambda: 2)
        b = Thunk(lambda: 2)

        self.assertEqual(a, b)

        self.assertEqual(a, 2)
        self.assertEqual(b, 2)

    def test_ne_value(self):
        a = Thunk(lambda: 2)
        b = Thunk(lambda: 3)

        self.assertNotEqual(a, b)

        self.assertNotEqual(a, 3)
        self.assertNotEqual(b, 2)

    def test_lt_value(self):
        a = Thunk(lambda: 2)
        b = Thunk(lambda: 3)

        self.assertLess(a, b)
        self.assertLess(a, 3)

    def test_gt_value(self):
        a = Thunk(lambda: 2)
        b = Thunk(lambda: 3)

        self.assertGreater(b, a)
        self.assertGreater(b, 2)

    def test_le_value(self):
        a = Thunk(lambda: 2)
        b = Thunk(lambda: 3)
        c = Thunk(lambda: 2)

        self.assertLessEqual(a, b)
        self.assertLessEqual(a, c)
        self.assertLessEqual(a, 3)
        self.assertLessEqual(a, 2)

    def test_ge_value(self):
        a = Thunk(lambda: 3)
        b = Thunk(lambda: 2)
        c = Thunk(lambda: 2)

        self.assertGreaterEqual(a, b)
        self.assertGreaterEqual(a, c)
        self.assertGreaterEqual(a, 3)
        self.assertGreaterEqual(a, 2)
