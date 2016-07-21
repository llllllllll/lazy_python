import sys

from lazy import data
from lazy._thunk import thunk, strict, get_children, operator
from lazy._undefined import undefined
from lazy.bytecode import lazy_function
from lazy.include import get_include
from lazy.runtime import run_lazy
from lazy.tree import parse

__version__ = '0.2.1'


def load_ipython_extension(ipython):  # pragma: no cover

    def lazy_magic(line, cell=None):
        return run_lazy(
            line + '\n' + (cell or ''),
            mode='exec' if cell is not None else 'eval',
            globals_=ipython.user_ns
        )

    ipython.register_magic_function(lazy_magic, 'line_cell', 'lazy')


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
        assert fullname == 'lazy.operator', 'ayyy lmao'
        sys.modules[fullname] = operator
        return operator
sys.meta_path.append(operator_importer())
del operator_importer


__all__ = [
    'run_lazy',
    'lazy_function',
    'thunk',
    'data',
    'get_children',
    'get_include',
    'operator',
    'parse',
    'undefined',
    'strict',
]
