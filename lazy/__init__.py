import sys

from lazy import data
from lazy._thunk import thunk, strict, get_children, operator
from lazy._undefined import undefined
from lazy.bytecode import lazy_function
from lazy.include import get_include
from lazy.runtime import run_lazy
from lazy.tree import LTree

__version__ = '0.1.12'


class operator_importer:
    """Metapath finder and loader to remap ``lazy._thunk.operator`` to
    ``lazy.operator``.
    """

    def find_module(self, fullname, path=None):
        return self if fullname == 'lazy.operator' else None

    def load_module(self, fullname):
        try:
            return sys.modules[fullname]
        except KeyError:
            pass
        if fullname == 'lazy.operator':
            sys.modules[fullname] = operator
            return operator
        raise AssertionError('ayy lmao')
sys.meta_path.append(operator_importer())
del operator_importer


__all__ = [
    'LTree',
    'run_lazy',
    'lazy_function',
    'thunk',
    'data',
    'get_children',
    'get_include',
    'operator',
    'undefined',
    'strict',
]
