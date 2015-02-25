from unittest import TestCase

from lazy import thunk, strict, lazy_function


# We decorate with strict so that the module loads, nose is a bitch.
@strict
@lazy_function
def f(a, b):
    return a + b


class LazyFunctionTestCase(TestCase):
    def test_is_lazy(self):
        self.assertIsInstance(f(1, 2), thunk)

    def test_not_decorator(self):
        def g(a, b):
            return a - b

        g = lazy_function(g)

        self.assertIsInstance(g(1, 2), thunk)

    def test_lazy_call(self):
        called = False

        @lazy_function
        def g():
            nonlocal called
            called = True

        result = g()
        self.assertFalse(called, 'The function call was strict')

        strict(result)
        self.assertTrue(called, 'The function call did not evaluate')

    def test_is(self):
        @lazy_function
        def g():
            return 1 is 1

        a = g()
        self.assertIsInstance(a, thunk)
        self.assertTrue(strict(a))

        @lazy_function
        def h(a):
            return a is None

        b = h(None)
        self.assertIsInstance(b, thunk)
        self.assertTrue(strict(b))

        c = h('not none')
        self.assertIsInstance(c, thunk)
        self.assertFalse(strict(c))

    def test_not(self):
        @lazy_function
        def g():
            return not 1

        a = g()
        self.assertIsInstance(a, thunk)
        self.assertFalse(strict(a))

        @lazy_function
        def h(a):
            return not a

        b = h(False)
        self.assertIsInstance(b, thunk)
        self.assertTrue(strict(b))

        c = h(True)
        self.assertIsInstance(c, thunk)
        self.assertFalse(strict(c))
