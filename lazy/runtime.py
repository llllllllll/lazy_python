import ast
from ctypes import pythonapi, c_int, py_object
from inspect import getsourcelines
from six import iteritems
from sys import _getframe, settrace, gettrace

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

    for k, v in iteritems(namespace):
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


class _LazyContextExit(Exception):
    """
    Exception raised to bail of of the lazy context manager without executing
    the code.
    """
    pass


def _dummy_trace(stackframe, event, arg):
    """
    Used to enable tracing.
    """
    pass


class LazyContext(object):
    """
    Context manager for creating a block of lazy code from within
    strict python.
    This is a dirty hack, why am I doing this.

    WARNING: You cannot use LazyContext with other context managers.
    If you want to use another context manager inside of a LazyContext,
    do:

    with LazyContext():
        with OtherContext():
            # code
            pass
    """
    def __init__(self):
        self._enter_lno = None
        self._exit_lno = None
        self._tracefn = None
        self._exc = None
        self._prevframe = None
        self._oldf_trace = None
        self._oldtrace = None

    def __enter__(self):
        prev_frame = _getframe().f_back
        self._prevframe = prev_frame
        self._enter_lno = prev_frame.f_lineno
        self._exc = _LazyContextExit()
        self._oldtrace = gettrace()
        settrace(_dummy_trace)

        # Set the trace function of the previous frame to be
        # our exception raiser. This makes us jump over the body
        # of the context manager without executing it.
        # This will let us get the line number where it exits.
        prev_frame.f_trace = self._raiser_trace

    def _raiser_trace(self, stackframe, event, arg):
        """
        Raises our exception instance.
        """
        raise self._exc

    def __exit__(self, exc_type, exc_value, exc_tb):
        prev_frame = self._prevframe

        # we only need to reset the global trace function.
        # Resetting the local trace function causes some strange
        # behaviour with f_lineno.
        settrace(self._oldtrace)

        if exc_value is not self._exc:
            # This should never happen; however, this is to be
            # safe and to make sure we know what is going on.
            return False

        filename = prev_frame.f_code.co_filename
        exit_lno = prev_frame.f_lineno

        with open(filename) as f:
            # This slice _should_ exist since we grabbed them
            # from this file.
            src_lines = f.readlines()[self._enter_lno:exit_lno]

        locals_overrides = set()
        globals_ = dict(prev_frame.f_globals)
        for k, v in iteritems(prev_frame.f_locals):
            if k in globals_:
                locals_overrides.add(k)
            globals_[k] = v

        try:
            run_lazy(
                _fix_scope(src_lines, self._enter_lno),
                name=filename,
                globals=globals_,
                locals=prev_frame.f_locals,
            )
        finally:
            # update the globals
            for k, v in iteritems(globals_):
                if k not in locals_overrides:
                    prev_frame.f_globals[k] = v
            # update the frame locals to account for the code we just executed.
            pythonapi.PyFrame_LocalsToFast(py_object(prev_frame), c_int(1))

        return True


try:
    __IPYTHON__
except NameError:
    __IPYTHON__ = False


if __IPYTHON__:

    from IPython.core.magic import register_cell_magic

    @register_cell_magic
    def lazy(line, cell):
        run_lazy(cell)
