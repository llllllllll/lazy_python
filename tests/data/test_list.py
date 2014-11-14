from unittest import TestCase

from lazy import undefined
from lazy.data import LazyList, nil, Cons


class LazyListTestCase(TestCase):
    def test_lazy_index(self):
        ls = Cons(undefined, Cons(2, Cons(undefined, nil)))
        self.assertEqual(ls[1], 2)

    def test_LazyList_abstract(self):
        with self.assertRaises(TypeError):
            LazyList()

    def test_iter(self):
        for e, v in enumerate(Cons(0, Cons(1, Cons(2, Cons(3, nil))))):
            self.assertEqual(e, v)
