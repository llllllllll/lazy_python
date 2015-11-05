from abc import ABCMeta, abstractmethod
from itertools import islice
from operator import index

from lazy._thunk import strict


class LMeta(ABCMeta):
    def __getitem__(self, literal):
        if not isinstance(literal, tuple):
            raise TypeError('invalid L literal')

        if not literal:
            return nil

        if len(literal) in (2, 3, 4) and literal[1] is ...:
            return _from_iter(_enum_from_to_by(literal[0], *literal[2:]))

        return _from_iter(iter(literal))


class L(metaclass=LMeta):
    def __repr__(self):
        return repr(strict(self))

    def __str__(self):
        return str(strict(self))

    @abstractmethod
    def __strict__(self):
        raise NotImplementedError('__strict__')

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError('__getitem__')

    @abstractmethod
    def __len__(self, key):
        raise NotImplementedError('__len__')

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError('__iter__')

    def __eq__(self, other):
        return strict(self) == strict(other)


@object.__new__
class nil(L):
    def __new__(cls):
        raise TypeError("cannot create 'nil' instances")

    def __strict__(self):
        return ()

    def __getitem__(self, key):
        raise IndexError('LazyList index out of range')

    def __len__(self):
        return 0

    def __iter__(self):
        return iter(())

    def __call__(self):
        return self

    def count(self, elem):
        return 0

    def index(self, value, start=None, stop=None):
        raise ValueError("'%s' not in list" % value)


class Cons(L):
    __slots__ = '_car', '_cdr', '_cdr_callable'

    def __init__(self, car, cdr):
        self._car = car
        self._cdr_callable = (lambda: cdr) if isinstance(cdr, Cons) else cdr

    @property
    def car(self):
        return self._car

    @property
    def cdr(self):
        try:
            return self._cdr
        except AttributeError:
            self._cdr = cdr = self._cdr_callable()
            return cdr

    def __strict__(self):
        try:
            return self._strict
        except AttributeError:
            self._strict = ns = (strict(self.car),) + strict(self.cdr)
            return ns

    def __getitem__(self, key):
        if isinstance(key, slice):
            return _from_iter(
                islice(iter(self), key.start, key.stop, key.step),
            )

        key = strict(index(key))
        if key < 0:
            key = len(self) + key

        if key == 0:
            return self.car
        else:
            return self.cdr[key - 1]

    def __len__(self):
        return len(strict(self))

    def __iter__(self):
        a = self
        while a is not nil:
            yield a.car
            a = a.cdr

    def count(self, value):
        l = self
        count = 0
        while l is not nil:
            count += l.car == value
            l = l.cdr
        return count

    def index(self, value, start=None, stop=None):
        start = index(start) if start is not None else 0
        if stop is not None:
            stop = index(stop)
        if not (start == 0 and stop is None):
            l = self[start:stop]
        else:
            l = self
        idx = start
        while l is not nil:
            if l.car == value:
                return idx
            l = l.cdr
            idx += 1
        raise ValueError("'%s' not in list" % value)


def _enum_from_to_by(from_, to=None, by=1):
    if to is not None:
        while from_ <= to:
            yield from_
            from_ += by
    else:
        while True:
            yield from_
            from_ += by


def _from_iter(it):
    try:
        car = next(it)
    except StopIteration:
        return nil

    return Cons(car, lambda: _from_iter(it))
