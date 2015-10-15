from sys import _getframe

from codetransformer import Code

from .bytecode import lazy_function


def run_lazy(src, name='<string>', mode='exec', globals_=None, locals_=None):
    if mode == 'exec':
        f = exec
    elif mode == 'eval':
        f = eval
    else:
        raise ValueError("mode must be either 'exec' or 'eval'")
    return f(
        lazy_function.transform(Code.from_pycode(
            compile(src, name, mode),
        )).to_pycode(),
        _getframe().f_back.f_globals if globals_ is None else globals_,
        _getframe().f_back.f_locals if locals_ is None else locals_,
    )


try:
    __IPYTHON__
except NameError:
    __IPYTHON__ = False


if __IPYTHON__:

    from IPython.core.magic import register_line_cell_magic

    @register_line_cell_magic
    def lazy(line, cell=None):
        return run_lazy(
            line + '\n' + (cell or ''),
            mode='exec' if cell is not None else 'eval',
            globals_=get_ipython().user_ns  # noqa
        )
