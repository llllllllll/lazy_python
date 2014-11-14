from unittest import TestCase

from lazy import seq, strict, Thunk
from lazy.data.empty import EmptyObject


class SeqTestCase(TestCase):
    def test_strict(self):
        self.assertEqual(strict(5), 5)
        self.assertEqual(Thunk(lambda: 5), 5)

    def test_seq(self):
        self.assertEqual(seq(1, 2), 2)

        mutable = EmptyObject()

        def mutator(a):
            mutable.a = a

        a = 5

        self.assertEqual(seq(Thunk(mutator, a), 2), 2)
        self.assertEqual(mutable.a, a)
