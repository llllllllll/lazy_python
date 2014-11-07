import ast
from inspect import getsource
from six import iteritems
from sys import _getframe
from textwrap import dedent

from lazy.transformer import LazyTransformer
from lazy.thunk import Thunk


def run_lazy(src, name='<string>', globals=None, locals=None):
    optimus_prime = LazyTransformer()
    code_obj = compile(optimus_prime.visit(ast.parse(src)), name, 'exec')

    globals = _getframe().f_back.f_globals if globals is None else globals
    locals = _getframe().f_back.f_locals if locals is None else locals

    # Add the names for Thunk to be used by the runtime environment.
    globals[optimus_prime.THUNK] = Thunk
    exec(code_obj, globals, locals)


def lazy_function(f):
    """
    Makes a function lazy.
    """
    # The list of names bound the this function.
    lazy_names = []

    # Get the namespace of the calling frame.
    calling_frame = _getframe().f_back
    namespace = dict(calling_frame.f_globals)
    namespace.update(calling_frame.f_locals)

    for k, v in iteritems(namespace):
        if v is lazy_function:
            lazy_names.append('@' + k)

    if not lazy_names:
        raise ValueError('Cannot find lazy_function')

    # We need to purge all instances of THIS function from the decorator list
    # to prevent infinite recursion when we exec lazified code.
    src = dedent(getsource(f))
    src = '\n'.join(
        l for l in src.splitlines() if l not in lazy_names
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
