import copy
import math
import operator
from six import iteritems


def _maybe_strict(v):
    """
    Gets the strict value from a Thunk or concrete value.
    """
    if isinstance(v, Thunk):
        return v.strict
    return v


def _safesetattr(obj, attr, value):
    """
    Because we are overriding __setattr__, we need a
    non-recursive way of setting attributes.

    This is to be used to set attributes internally.
    """
    object.__setattr__(obj, attr, value)


class Thunk(object):
    """
    A defered computation.
    This can be used wherever a strict value is used (maybe?)
    """
    def __init__(self, function, *args, **kwargs):
        _safesetattr(self, '_function', function)
        _safesetattr(self, '_args', args)
        _safesetattr(self, '_kwargs', kwargs)

    @property
    def strict(self):
        """
        The strict value. This computes the value and stores it.
        """
        return self._compute()

    def _compute(self):
        """
        Actually get the value and store it.
        """
        # Strictly evaluate the args and kwargs.
        args = [_maybe_strict(arg) for arg in self._args]
        kwargs = {k: _maybe_strict(v) for k, v in iteritems(self._kwargs)}

        # The function could be a Thunk too, like (a + b)(arg)
        function = _maybe_strict(self._function)

        # Compute the strict value.
        strict = function(*args, **kwargs)

        # memoize this computation.
        _safesetattr(self, '_compute', lambda: strict)
        return strict

    # Override all the sensible magic methods.

    def __eq__(self, other):
        return Thunk(operator.eq, self, other)

    def __ne__(self, other):
        return Thunk(operator.neq, self, other)

    def __lt__(self, other):
        return Thunk(operator.lt, self, other)

    def __gt__(self, other):
        return Thunk(operator.gt, self, other)

    def __le__(self, other):
        return Thunk(operator.le, self, other)

    def __ge__(self, other):
        return Thunk(operator.ge, self, other)

    def __pos__(self):
        return Thunk(operator.pos, self)

    def __neq__(self):
        return Thunk(operator.neg, self)

    def __abs__(self):
        return Thunk(abs, self)

    def __invert__(self):
        return Thunk(operator.invert, self)

    def __round__(self):
        return Thunk(round, self)

    def __floor__(self):
        return Thunk(math.floor, self)

    def __ceil__(self):
        return Thunk(math.ceil, self)

    def __trunc__(self):
        return Thunk(math.trunc, self)

    def __add__(self, other):
        return Thunk(operator.add, self, other)
    __radd__ = __add__
    __iadd__ = __add__

    def __sub__(self, other):
        return Thunk(operator.sub, self, other)
    __rsub__ = __sub__
    __isub__ = __sub__

    def __mul__(self, other):
        return Thunk(operator.mul, self, other)
    __rmul__ = __mul__
    __imul__ = __mul__

    def __floordiv__(self, other):
        return Thunk(operator.floordiv, self, other)
    __rfloordiv__ = __floordiv__
    __ifloordiv__ = __floordiv__

    def __div__(self, other):
        return Thunk(operator.div, self, other)
    __rdiv__ = __div__
    __idiv__ = __div__

    def __mod__(self, other):
        return Thunk(operator.mod, self, other)
    __rmod__ = __mod__
    __imod__ = __mod__

    def __divmod__(self, other):
        return Thunk(divmod, self, other)
    __rdivmod__ = __divmod__
    __idivmod__ = __divmod__

    def __pow__(self, other):
        return Thunk(pow, self, other)
    __rpow__ = __pow__
    __ipow__ = __pow__

    def __lshift__(self, other):
        return Thunk(operator.lshift, self, other)
    __rlshift__ = __lshift__
    __ilshift__ = __lshift__

    def __rshift__(self, other):
        return Thunk(operator.rshift, self, other)
    __rrshift__ = __rshift__
    __irshift__ = __rshift__

    def __and__(self, other):
        return Thunk(operator.and_, self, other)
    __rand__ = __and__
    __iand__ = __and__

    def __or__(self, other):
        return Thunk(operator.or_, self, other)
    __ror__ = __or__
    __ior__ = __or__

    def __xor__(self, other):
        return Thunk(operator.xor, self, other)
    __rxor__ = __xor__
    __ixor__ = __xor__

    def __int__(self):
        return int(self.strict)

    def __float__(self):
        return float(self.strict)

    def __complex__(self):
        return complex(self.strict)

    def __oct__(self):
        return oct(self.strict)

    def __hex__(self):
        return hex(self.strict)

    def __index__(self):
        return Thunk(lambda: self.strict.__index__)

    def __str__(self):
        return str(self.strict)

    def __bytes__(self):
        return bytes(self.strict)

    def __repr__(self):
        return repr(self.strict)

    def __format__(self, formatstr):
        return self.strict.__format__(formatstr)

    def __hash__(self):
        return hash(self.strict)

    def __bool__(self):
        return bool(self.strict)

    def __dir__(self):
        return dir(self.strict)

    def __getattr__(self, name):
        return Thunk(operator.attrgetter(name), self.strict)

    def __setattr__(self, name, value):
        return Thunk(lambda: setattr(self.strict, name, value))

    def __delattr__(self, name):
        return Thunk(lambda: delattr(self.strict, name))

    def __len__(self):
        return Thunk(len, self)

    def __getitem__(self, key):
        return Thunk(operator.itemgetter(key), self.strict)

    def __setitem__(self, key,  value):
        return Thunk(lambda: operator.setitem(self.strict, key, value))

    def __delitem__(self, key):
        return Thunk(lambda: operator.delitem(self.strict, key))

    def __iter__(self):
        return iter(self.strict)

    def __reversed__(self):
        return reversed(self.strict)

    def __contains__(self, item):
        return Thunk(lambda: item in self.strict)

    def __missing__(self, key):
        return Thunk(lambda: self.strict.__missing__(key))

    def __instancecheck__(self, instance):
        return Thunk(lambda: isinstance(instance, self.strict))

    def __subclasscheck__(self, subclass):
        return Thunk(lambda: issubclass(subclass, self.strict))

    def __call__(self, *args, **kwargs):
        return Thunk(self, *args, **kwargs)

    def __enter__(self):
        return self.strict.__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.strict.__exit__(exc_type, exc_value, exc_tb)

    def __get__(self, instance, owner):
        return Thunk(lambda: self.strict.__get__(instance, owner))

    def __set__(self, instance, value):
        return Thunk(lambda: self.strict.__set__(instance, value))

    def __delete__(self, instance):
        return Thunk(lambda: self.strict.__delete__(instance))

    def __copy__(self):
        return copy.copy(self.strict)

    def __deepcopy__(self, memodict={}):
        return copy.deepcopy(self)
