from abc import ABCMeta, abstractmethod
from six import with_metaclass

from lazy.thunk import Thunk
from lazy.utils import strict, singleton


class LazyList(with_metaclass(ABCMeta)):
    def __repr__(self):
        return repr(self.strict)

    def __str__(self):
        return str(self.strict)

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError('__getitem__')

# LazyLists are sort of like thunks.
Thunk.register(LazyList)


@singleton
class NilType(LazyList):
    def __init__(self):
        pass

    @property
    def strict(self):
        return ()

    def __getitem__(self, key):
        raise IndexError('LazyList index out of range')

nil = NilType()


class Cons(LazyList):
    def __init__(self, car, cdr):
        self._car = car
        self._cdr = cdr

    @property
    def strict(self):
        return self._normal_form()

    def _normal_form(self):
        ns = (strict(self._car),) + strict(self._cdr)
        self._normal_form = lambda: ns
        return ns

    def __getitem__(self, key):
        key = strict(key.__index__())
        if key == 0:
            return self._car
        else:
            return self._cdr[key - 1]
