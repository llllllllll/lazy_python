import ast
from inspect import getsource
from six import iteritems
from sys import _getframe

from lazy.transformer import LazyTransformer
from lazy.thunk import Thunk


def run_lazy(src, name='<string>', globals=None, locals=None):
    optimus_prime = LazyTransformer()
    code_obj = compile(optimus_prime.visit(ast.parse(src)), name, 'exec')

    globals = _getframe().f_back.f_globals if globals is None else globals
    locals = _getframe().f_back.f_locals if locals is None else locals

    # Add the think name.
    globals[optimus_prime.THUNK] = Thunk
    exec(code_obj, globals, locals)


def lazy_function(f):
    """
    Makes a function lazy.
    """
    lazy_names = []
    for k, v in iteritems(f.__globals__):
        if v is lazy_function:
            lazy_names.append('@' + k)

    if not lazy_names:
        raise ValueError('Cannot find lazy_function')

    src = '\n'.join(
        l for l in getsource(f).splitlines() if l not in lazy_names
    )

    locals_ = {}
    run_lazy(
        src,
        name=f.__code__.co_filename,
        globals=dict(f.__globals__),
        locals=locals_,
    )
    return locals_[f.__name__]
