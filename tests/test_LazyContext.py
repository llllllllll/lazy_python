from unittest import TestCase

from lazy.runtime import LazyContext


class EmptyObject(object):
    """
    object with a __dict__.
    """
    pass


class LazyContextTestCase(TestCase):
    def test_locals_reasssign(self):
        updated = False

        with LazyContext():
            updated = True

        self.assertTrue(updated)

    def test_locals_del(self):
        name_error = None

        with LazyContext():
            del name_error

        with self.assertRaises(NameError):
            name_error  # NOQA

    def test_globals(self):
        with LazyContext():
            EmptyObject()
