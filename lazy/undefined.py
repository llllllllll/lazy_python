from lazy.thunk import Thunk
from lazy.utils import singleton


@Thunk.register
@singleton
class UndefinedValue(Exception):
    """
    An undefined value.
    You cannot strictly evaluate this
    """
    @property
    def strict(self):
        raise self

    def __str__(self):
        return 'undefined'
    __repr__ = __str__


undefined = UndefinedValue()
