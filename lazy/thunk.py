from abc import ABCMeta
import math
import operator
from six import iteritems, itervalues, with_metaclass, PY2

from lazy.seq import strict
from lazy.utils import (
    isolate_namespace,
    safesetattr,
    safegetattr,
    is_dunder,
)


# Isolated attribute names.
_function_name = isolate_namespace('_function')
_args_name = isolate_namespace('_args')
_kwargs_name = isolate_namespace('_kwargs')


class MagicExpansionMeta(ABCMeta):
    """
    A metaclass for expanding the @reflected and @inplace decorators.
    """
    def __new__(mcls, name, bases, dict_):
        for v in itervalues(dict(dict_)):
            aliases = getattr(v, '_aliases', ())
            for alias in aliases:
                dict_[alias] = v

        return super(MagicExpansionMeta, mcls).__new__(
            mcls, name, bases, dict_,
        )


def _alias(f, prefix):
    name = f.__name__
    if not is_dunder(name):
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


def strict_lookup(m):
    """
    Decorator that says that this method needs to be looked up
    strictly.
    """
    strict_lookup.strict_names.add(m.__name__)
    return m
strict_lookup.strict_names = set()


class Thunk(with_metaclass(MagicExpansionMeta)):
    """
    A defered computation.
    This can be used wherever a strict value is used (maybe?)

    This represents the weak head normal form of an expression.
    """
    def __init__(self, function, *args, **kwargs):
        safesetattr(self, _function_name, function)
        safesetattr(self, _args_name, args)
        safesetattr(self, _kwargs_name, kwargs)

    @property
    @strict_lookup
    def strict(self):
        """
        The strict value. This computes the value and stores it.
        """
        return safegetattr(self, '_normal_form')()

    def _normal_form(self):
        """
        Return the normal form of the thunk.
        """
        # Strictly evaluate the args and kwargs.
        args = [strict(arg) for arg in safegetattr(self, _args_name)]
        kwargs = {k: strict(v)
                  for k, v in iteritems(safegetattr(self, _kwargs_name))}

        # The function could be a Thunk too, like (a + b)(arg)
        function = strict(safegetattr(self, _function_name))

        # Compute the strict value.
        normal_form = function(*args, **kwargs)
        while isinstance(normal_form, Thunk):
            # Make sure that we have actually made this strict.
            normal_form = safegetattr(normal_form, 'strict')

        # memoize this computation.
        safesetattr(self, '_normal_form', lambda: strict)
        return normal_form

    # Override all the sensible magic methods.

    @property
    @strict_lookup
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
        return self.strict.__index__()

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
        if name in strict_lookup.strict_names:
            return safegetattr(self, name)

        return Thunk(getattr, self, name)

    def __setattr__(self, name, value):
        setattr(self.strict, strict(name), value)

    def __delattr__(self, name):
        return delattr(self.strict, strict(name))

    def __len__(self):
        return Thunk(len, self)

    def __getitem__(self, key):
        return Thunk(Thunk(operator.itemgetter, key), self)

    def __setitem__(self, key, value):
        self.strict[strict(key)] = value

    def __delitem__(self, key):
        del self.strict[strict(key)]

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

    def __prepare__(self, name, bases):
        return self.strict.__prepare__(name, bases)

    def __next__(self):
        return Thunk(lambda: next(self.strict))

    # PY2 support:
    if PY2:
        __nonzero__ = __bool__
        # I can probably leave this; however, this is not the py2 convention.
        del __bool__

        def __coerce__(self, other):
            return self.strict.__coerce__(other)
