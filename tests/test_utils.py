from nose_parameterized import parameterized
from unittest import TestCase

from lazy.utils import (
    safesetattr,
    safegetattr,
    isolate_namespace,
    is_dunder,
    singleton,
)


class UtilsTestCase(TestCase):
    def test_safesetattr(self):
        class NoSetAttr(object):
            def __setattr__(self, name, value):
                raise NotImplementedError('__setattr__')

        with self.assertRaises(NotImplementedError):
            NoSetAttr().test = 'test'

        safesetattr(NoSetAttr(), 'test', 'test')

    def test_safegetattr(self):
        class NoGetAttr(object):
            test = 'test'

            def __getattribute__(self, name):
                raise NotImplementedError('__getattr__')

        with self.assertRaises(NotImplementedError):
            NoGetAttr().test

        self.assertEqual(safegetattr(NoGetAttr(), 'test'), 'test')

    def test_isolate_namespace(self):
        self.assertNotEqual('test', isolate_namespace('test'))

    @parameterized.expand([
        ('false', False),
        ('_false', False),
        ('__false', False),
        ('false_', False),
        ('false__', False),
        ('_false_', False),
        ('__false_', False),
        ('_false__', False),
        ('__dunder__', True),
    ])
    def test_is_dunder(self, name, expected):
        self.assertEqual(is_dunder(name), expected)

    def test_singleton(self):
        @singleton
        class S(object):
            pass

        self.assertIs(S(), S())
