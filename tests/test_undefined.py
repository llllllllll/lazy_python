from unittest import TestCase

from lazy import undefined, strict


class UndefinedTestCase(TestCase):
    def test_lazy(self):
        undefined

    def test_cannot_strict(self):
        with self.assertRaises(undefined.__class__):
            strict(undefined)
