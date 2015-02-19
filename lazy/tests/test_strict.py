from unittest import TestCase

from lazy import strict, thunk


class StrictTestCase(TestCase):
    def test_strict(self):
        self.assertIs(strict(5), 5)
        self.assertEqual(thunk(lambda: 5), 5)
