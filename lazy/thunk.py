import math
import operator
from six import iteritems, itervalues, with_metaclass

from lazy.utils import isolate_namespace


# Isolated attribute names.
_function_name = isolate_namespace('_function')
_args_name = isolate_namespace('_args')
_kwargs_name = isolate_namespace('_kwargs')


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


def _safegetattr(obj, name, *default):
    """
    Because we are overridding __getattr__, we need a
    non-recursive way of getting attributes.

    This is used to get attributes internally.
    """
    return object.__getattribute__(obj, name, *default)


class MagicExpansionMeta(type):
    """
    A metaclass for expanding the @reflected and @inplace decorators.
    """
    def __new__(mcls, name, bases, dict_):
        for v in itervalues(dict(dict_)):
            aliases = getattr(v, '_aliases', ())
            for alias in aliases:
                dict_[alias] = v

        return type.__new__(mcls, name, bases, dict_)


def _alias(f, prefix):
    name = f.__name__
    if not (name.startswith('__') and name.endswith('__')):
        raise ValueError('%s must be a dunder method' % name)

    name = name[2:-2]
    aliases = getattr(f, '_aliases', set())
    aliases.add('__%s%s__' % (prefix, name))
    f._aliases = aliases


def reflected(f):
    """
    Aliases this magic with the reflected version.
    """
    _alias(f, 'r')
    return f


def inplace(f):
    """
    Aliases this magic with the inplace version.
    """
    _alias(f, 'i')
    return f


class Thunk(with_metaclass(MagicExpansionMeta)):
    """
    A defered computation.
    This can be used wherever a strict value is used (maybe?)
    """
    def __init__(self, function, *args, **kwargs):
        _safesetattr(self, _function_name, function)
        _safesetattr(self, _args_name, args)
        _safesetattr(self, _kwargs_name, kwargs)

    @property
    def strict(self):
        """
        The strict value. This computes the value and stores it.
        """
        return _safegetattr(self, '_compute')()

    def _compute(self):
        """
        Actually get the value and store it.
        """
        # Strictly evaluate the args and kwargs.
        args = [_maybe_strict(arg) for arg in _safegetattr(self, _args_name)]
        kwargs = {k: _maybe_strict(v)
                  for k, v in iteritems(_safegetattr(self, _kwargs_name))}

        # The function could be a Thunk too, like (a + b)(arg)
        function = _maybe_strict(_safegetattr(self, _function_name))

        # Compute the strict value.
        strict = function(*args, **kwargs)

        # memoize this computation.
        _safesetattr(self, '_compute', lambda: strict)
        return strict

    # Override all the sensible magic methods.

    @property
    def __class__(self):
        return self.strict.__class__

    def __eq__(self, other):
        return Thunk(operator.eq, self, other)

    def __ne__(self, other):
        return Thunk(operator.ne, self, other)

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

    def __neg__(self):
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

    @reflected
    @inplace
    def __add__(self, other):
        return Thunk(operator.add, self, other)

    @reflected
    @inplace
    def __sub__(self, other):
        return Thunk(operator.sub, self, other)

    @reflected
    @inplace
    def __mul__(self, other):
        return Thunk(operator.mul, self, other)

    @reflected
    @inplace
    def __floordiv__(self, other):
        return Thunk(operator.floordiv, self, other)

    @reflected
    @inplace
    def __div__(self, other):
        return Thunk(operator.div, self, other)

    @reflected
    @inplace
    def __truediv__(self, other):
        return Thunk(operator.truediv, self, other)

    @reflected
    @inplace
    def __mod__(self, other):
        return Thunk(operator.mod, self, other)

    @reflected
    @inplace
    def __divmod__(self, other):
        return Thunk(divmod, self, other)

    @reflected
    @inplace
    def __pow__(self, other):
        return Thunk(pow, self, other)

    @reflected
    @inplace
    def __lshift__(self, other):
        return Thunk(operator.lshift, self, other)

    @reflected
    @inplace
    def __rshift__(self, other):
        return Thunk(operator.rshift, self, other)

    @reflected
    @inplace
    def __and__(self, other):
        return Thunk(operator.and_, self, other)

    @reflected
    @inplace
    def __or__(self, other):
        return Thunk(operator.or_, self, other)

    @reflected
    @inplace
    def __xor__(self, other):
        return Thunk(operator.xor, self, other)

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

    def __getattribute__(self, name):
        try:
            return _safegetattr(self, name)
        except AttributeError:
            return getattr(self.strict, _maybe_strict(name))

    def __setattr__(self, name, value):
        return _safesetattr(
            self.strict, _maybe_strict(name), _maybe_strict(value),
        )

    def __delattr__(self, name):
        return delattr(self.strict, _maybe_strict(name))

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
        return self.strict.__delete__(instance)
