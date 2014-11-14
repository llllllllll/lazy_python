from unittest import TestCase

from lazy.runtime import LazyContext
from lazy.data.empty import EmptyObject


class LazyContextTestCase(TestCase):
    def test_locals_reasssign(self):
        updated = False

        with LazyContext():
            updated = True

        self.assertTrue(updated)

    def test_lazy(self):
        mutable = EmptyObject()

        def impure_disgusting_function(a):
            mutable.a = a

        a = 5
        with LazyContext():
            impure_disgusting_function(a)

        self.assertFalse(hasattr(mutable, 'a'))

        with LazyContext():
            impure_disgusting_function(a).strict

        self.assertEquals(mutable.a, a)

    def test_locals_del(self):
        name_error = None

        with LazyContext():
            del name_error

        with self.assertRaises(NameError):
            name_error  # NOQA

    def test_globals(self):
        with LazyContext():
            EmptyObject()
