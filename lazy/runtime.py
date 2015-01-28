import ast
from inspect import getsourcelines
from sys import _getframe

from lazy.transformer import LazyTransformer
from lazy._thunk import thunk


def run_lazy(src, name='<string>', globals=None, locals=None):
    optimus_prime = LazyTransformer()
    code_obj = compile(optimus_prime.visit(ast.parse(src)), name, 'exec')

    globals = _getframe().f_back.f_globals if globals is None else globals
    locals = _getframe().f_back.f_locals if locals is None else locals

    # Add the names for Thunk to be used by the runtime environment.
    globals[optimus_prime.THUNK] = thunk
    exec(code_obj, globals, locals)


def _fix_scope(src_lines, lines):
    """
    Fixes the 'scope' of some source code by prepending lines empty
    lines and wrapping it in an 'if True:' if needed.
    """
    if src_lines[0].startswith((' ', '\t')):
        header = ['if True:\n']
    else:
        header = ['\n']

    return ''.join(['\n'] * (lines - 1) + header + src_lines)


def lazy_function(f):
    """
    Makes a function lazy.

    This is better thought of as a macro that transforms the _source code_
    of the function.

    WARNING: This depends on being able to find the source for a function.
    Debuggers will blow up on lazy_functions.
    """
    # The list of names bound the this function.
    lazy_names = []

    # Get the namespace of the calling frame.
    calling_frame = _getframe().f_back
    namespace = dict(calling_frame.f_globals)
    namespace.update(calling_frame.f_locals)

    for k, v in namespace.items():
        if v is lazy_function:
            lazy_names.append('@' + k)

    if not lazy_names:
        raise ValueError('Cannot find lazy_function')

    # We need to purge all instances of THIS function from the decorator list
    # to prevent infinite recursion when we exec lazified code.
    src_lines, lno = getsourcelines(f)
    src = '\n'.join(
        l for l in _fix_scope(src_lines, lno).splitlines()
        if l not in lazy_names
    )

    locals_ = {}
    # Pass the source code of f to run_lazy. This will be executed to
    # construct a new function with the LazyTransformer modified ast.
    run_lazy(
        src,
        name=f.__code__.co_filename,
        globals=dict(f.__globals__),
        locals=locals_,
    )

    # Peek into the namespace we just exec'd the function in to grab the new
    # function object.
    return locals_[f.__name__]


try:
    __IPYTHON__
except NameError:
    __IPYTHON__ = False


if __IPYTHON__:

    from IPython.core.magic import register_cell_magic

    @register_cell_magic
    def lazy(line, cell):
        run_lazy(cell)
