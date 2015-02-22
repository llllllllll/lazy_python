import ast
from sys import _getframe

from lazy.transformer import LazyTransformer
from lazy._thunk import thunk


def run_lazy(src, name='<string>', globals_=None, locals_=None):
    transformer = LazyTransformer()
    code_obj = compile(transformer.visit(ast.parse(src)), name, 'exec')

    globals_ = _getframe().f_back.f_globals if globals_ is None else globals_
    locals_ = _getframe().f_back.f_locals if locals_ is None else locals_

    # Add the names for Thunk to be used by the runtime environment.
    globals_[transformer.THUNK_FROMVALUE] = thunk.fromvalue
    exec(code_obj, globals_, locals_)


try:
    __IPYTHON__
except NameError:
    __IPYTHON__ = False


if __IPYTHON__:

    from IPython.core.magic import register_cell_magic

    @register_cell_magic
    def lazy(line, cell):
        run_lazy(cell)
