from unittest import TestCase

from lazy import Thunk, lazy_function


@lazy_function
def f(a, b):
    return a + b


class LazyFunctionTestCase(TestCase):
    def test_is_lazy(self):
        self.assertIsInstance(f(1, 2), Thunk)

    def test_not_decorator(self):
        def g(a, b):
            return a - b

        g = lazy_function(g)

        self.assertIsInstance(g(1, 2), Thunk)
