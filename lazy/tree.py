from functools import reduce, partial
from itertools import chain
import operator as op

from codetransformer.utils.immutable import immutable

from ._thunk import thunk, get_children


_leaves = op.methodcaller('leaves')


class LTree(immutable):
    """A tree represnting a lazy expression.

    There are 2 node types:
      1. Call
      2. Normal

    A ``Call`` represents a lazy function call.
    A ``Normal`` node represents the value of an expression that has already
    been computed. This can come from ``thunk.fromexpr`` or just a literal
    that appears in your tree like: ``thunk(f, *args, **kwargs) + 1``
    This will be represented the same as:
    ``thunk(f, *args, **kwargs) + thunk.fromexpr(1)`
    where the 1 is stored as a ``Normal(value=1)`` node.

    To construct a new ``LTree``, use the ``parse`` class method.

    To turn an ``LTree`` back into an expression, we can use the ``lcompile``
    method.

    ``lcompile of LTree.parse`` is the identity.

    See Also
    --------
    Call
    Normal
    """
    __slots__ = ()

    @property
    def children(self):
        # This is not attrgetter(*self.__slots__)(self) because we still want
        # a tuple when `__slots__` has exactly 1 element.
        return tuple(getattr(self, s) for s in self.__slots__)

    def __new__(cls, *args, **kwargs):
        if cls is LTree:
            raise TypeError("Can't instantiate instances of %s" % cls.__name__)
        return super().__new__(cls)

    @classmethod
    def parse(cls, th):
        """Parse an ``LTree`` out of an object.

        Parameters
        ----------
        th : any
            The value to parse. If this is a ``thunk``, this will be unpacked.

        Returns
        -------
        t : LTree
            The tree form of this expression.

        Examples
        --------
        Working with non-thunks
        >>> LTree.parse(1)
        Normal(value=1)
        >>> LTree.parse(1 + 1)
        Normal(value=2)

        Working with thunks
        >>> from lazy import thunk
        >>> one = thunk.fromexpr(1)
        >>> LTree.parse(one)
        Normal(value=1)
        >>> LTree.parse(one + one)
        Call(func=Normal(value=<wrapped-function add>), args=(Normal(value=1), Normal(value=1)), kwargs={})  # noqa
        """
        if not isinstance(th, thunk):
            return Normal(th)

        children = get_children(th)
        if len(children) == 1:
            return Normal(children[0])

        func, args, kwargs = children
        parse = cls.parse
        return Call(
            parse(func),
            tuple(map(parse, args)),
            {k: parse(v) for k, v in kwargs.items()},
        )

    def lcompile(self, scope=None):
        scope = scope if scope is not None else {}
        try:
            return scope[self]
        except KeyError:
            pass

        return self._compile(scope)

    def __eq__(self, other):
        if not (isinstance(self, type(other)) and
                isinstance(other, type(self))):
            return False
        return self.children == other.children


class Call(LTree):
    """Node representing a lazy function call.

    Parameters
    ----------
    func : LTree
        The node representing the function to call.
    args : tuple[LTree]
        The nodes representing the positional arguments.
    kwargs : dict[str -> LTree]
        The nodes representing the keyword arguments.

    Notes
    -----
    The ``func`` is often a ``Normal``; however, it can be a ``Call` when
    the function is an expression like: ``compose(f, g)(*args)``
    """
    __slots__ = 'func', 'args', 'kwargs'

    def _compile(self, scope):

        def retrieve(term):
            try:
                return scope[term]
            except KeyError:
                scope[term] = ret = term._compile(scope)
                return ret

        scope[self] = ret = thunk(
            retrieve(self.func),
            *map(retrieve, self.args),
            **{k: retrieve(v) for k, v in self.kwargs.items()}
        )
        return ret

    def subs(self, substitutions):
        try:
            return substitutions[self]
        except KeyError:
            pass

        def retrieve(term):
            try:
                return substitutions[term]
            except KeyError:
                return term.subs(substitutions)

        return Call(
            retrieve(self.func),
            tuple(map(retrieve, self.args)),
            {k: retrieve(v) for k, v in self.kwargs.items()},
        )

    def leaves(self):
        yield from self.func.leaves()
        yield from chain.from_iterable(map(_leaves, self.args))
        yield from chain.from_iterable(map(_leaves, self.kwargs.values()))

    def __contains__(self, other):
        return (
            other == self or
            any(other in child for child in self.args) or
            any(other in child for child in self.kwargs.values())
        )

    def __hash__(self):
        return (
            hash(self.func) *
            hash(self.args) *
            reduce(op.mul, map(hash, self.kwargs.values()), 1)
        )

    def __str__(self):
        kwargs = ', '.join(map(partial(op.mod, '%s=%s'), self.kwargs.items()))
        return '%s(%s%s)' % (
            self.func,
            ', '.join(map(str, self.args)),
            (', %s' % kwargs) if kwargs else '',
        )


class Normal(LTree):
    """Node representing the normal form of an expression.

    Parameters
    ----------
    value : any
        The value of the expression.

    Notes
    -----
    This appears in the tree when you have a non-thunk object of a thunk
    whose value has already been computed.
    ``thunk.fromexpr`` generates pre-computed thunks.
    """
    __slots__ = 'value',

    def _compile(self, scope):
        scope[self] = ret = thunk.fromexpr(self.value)
        return ret

    def subs(self, substitutions):
        try:
            return substitutions[self]
        except KeyError:
            pass

        value = self.value
        try:
            value = substitutions[value]
        except (KeyError, TypeError):
            pass
        return Normal(value)

    def leaves(self):
        return self,

    def __contains__(self, other):
        return other == self or other == self.value

    def __hash__(self):
        type_hash = hash(type(self))
        value = self.value
        try:
            return hash(value) * type_hash
        except TypeError:
            return id(value) * type_hash

    def __str__(self):
        value = self.value
        try:
            return value.__name__
        except AttributeError:
            return repr(self.value)


parse = LTree.parse
lcompile = op.methodcaller('lcompile')


def fold_subexprs(expr):
    """Fold common subexpressions to memoize the intermediate results.

    Parameters
    ----------
    expr : any
        The expression to fold.

    Returns
    -------
    folded : thunk
        The folded expression

    Notes
    -----
    Things that rely on side-effects will not work as intended because each
    subexpression will be evaluated once.
    """
    return parse(expr).lcompile()
