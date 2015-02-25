from dis import Bytecode, opmap
from operator import is_, not_
from types import CodeType, FunctionType

from lazy._thunk import thunk, strict
from lazy.utils import isolate_namespace


def _getcode(func_or_code):
    if isinstance(func_or_code, CodeType):
        return func_or_code
    else:
        return func_or_code.__code__


class Opmap(dict):
    def __getattr__(self, name):
        return bytes((self[name],))

ops = Opmap(opmap)


def thunkify(tuple_, *, _thunk_=thunk):
    for t in tuple_ or ():
        yield _thunk_.fromvalue(t)


def _const_convert(c, _globals=None):
    if isinstance(c, CodeType):
        return LazyConverter(c, _globals).converted_code
    else:
        return thunk.fromvalue(c)


def _default(opcode, arg):
    """
    The default opcode behavior.
    """
    yield bytes((opcode,))
    if arg is not None:
        yield arg.to_bytes(2, 'little')


def _lazy_is(a, b, *, is_=is_):
    """
    Used instead of the `is` operator.
    """
    return thunk(is_, a, b)


def _lazy_not(a, *, not_=not_):
    """
    Used instead of the `not` operator.
    """
    return thunk(not_, a)


class LazyConverter(object):
    class Consts(object):
        def __init__(self):
            self._idx = 0
            self._obs = {}

        def index(self, ob):
            try:
                return self._obs[ob]
            except KeyError:
                self._obs[ob] = idx = self._idx.to_bytes(2, 'little')
                self._idx += 1
                return idx

        @property
        def contents(self):
            obs = self._obs
            return tuple(sorted(obs, key=lambda e: obs[e]))

    class LazyTransformations(dict):
        def __new__(cls, converter):
            return super().__new__(cls)

        def __init__(self, converter):
            self._converter = converter

        def __getitem__(self, opname):
            return getattr(
                self._converter, 'transform_' + opname, _default,
            )

        def __getattr__(self, opname):
            return self[opname]

    def __init__(self, f, _globals=None):
        self.f = f
        self.code = _getcode(f)

        # Construct the const objects.
        self._consts = self.Consts()
        for c in self.code.co_consts + (strict, thunk.fromvalue):
            self._consts.index(c)

        self.transformations = self.LazyTransformations(self)
        self._globals = _globals if _globals is not None else f.__globals__
        self._call_args_idx = None
        self._call_kwargs_idx = None
        self._co_total_argcount = None

    @property
    def converted_function(self):
        f = self.f

        return FunctionType(
            self.converted_code,
            f.__globals__,
            f.__name__,
            tuple(thunkify(f.__defaults__)),
            f.__closure__,
        )

    @property
    def converted_code(self):
        """
        Constructs a lazy code object.
        """
        co = self.code

        co_varnames = co.co_varnames + (
            isolate_namespace('_call_var'),
            isolate_namespace('_kwargs_var'),
        )

        len_co_varnames = len(co_varnames)
        self._call_kwargs_idx = (len_co_varnames - 1).to_bytes(2, 'little')
        self._call_args_idx = (len_co_varnames - 2).to_bytes(2, 'little')
        self._co_total_argcount = co.co_argcount + co.co_kwonlyargcount

        bc = b''.join(self._lazy_bytecode)

        return CodeType(
            co.co_argcount,
            co.co_kwonlyargcount,
            co.co_nlocals,
            co.co_stacksize + 1,
            co.co_flags,
            bc,
            self._consts.contents,
            co.co_names,
            co_varnames,
            co.co_filename,
            co.co_name,
            co.co_firstlineno,
            co.co_lnotab,
            co.co_freevars,
            co.co_cellvars,
        )

    @property
    def _lazy_bytecode(self):
        """
        Applies the lazy bytecode transformations.
        """
        for b in Bytecode(self.code):
            yield from self.transformations[b.opname](b.opcode, b.arg)

    def transform_MAKE_FUNCTION(self, opcode, arg):
        """
        Functions should have strict names.
        """
        yield ops.LOAD_CONST
        yield self._consts.index(strict)
        yield ops.ROT_TWO
        yield ops.CALL_FUNCTION
        yield b'\x01\x00'
        yield bytes((opcode,))
        yield arg.to_bytes(2, 'little')

    transform_MAKE_CLOSURE = transform_MAKE_FUNCTION

    def _transform_name(self, opcode, arg):
        """
        Loading a name immediatly wraps it in a `thunk`.
        """
        yield ops.LOAD_CONST
        yield self._consts.index(thunk.fromvalue)
        yield bytes((opcode,))
        yield arg.to_bytes(2, 'little')
        yield ops.CALL_FUNCTION
        yield b'\x01\x00'

    transform_LOAD_NAME = transform_LOAD_GLOBAL = _transform_name

    def transform_LOAD_FAST(self, opcode, arg):
        """
        Wrap arg lookups in thunks to be safe.
        """
        if arg > self._co_total_argcount:
            yield from _default(opcode, arg)
        else:
            yield from self._transform_name(opcode, arg)

    def transform_COMPARE_OP(self, opcode, arg):
        """
        Replace the `is` operator to act on the values the thunks represent.
        This makes `is` lazy.
        """
        if arg != 8:  # is
            yield from _default(opcode, arg)
            return

        yield ops.LOAD_CONST
        yield self._consts.index(_lazy_is)
        yield ops.ROT_THREE
        yield ops.CALL_FUNCTION
        yield b'\x02\x00'

    def transform_UNARY_NOT(self, opcode, arg):
        """
        Replace the `not` operator to act on the values that the thunks
        represent.
        This makes `not` lazy.
        """
        yield ops.LOAD_CONST
        yield self._consts.index(_lazy_not)
        yield ops.ROT_TWO
        yield ops.CALL_FUNCTION
        yield b'\x01\x00'


def lazy_function(f):
    """
    Creates a function whose body is lazily evaluated.
    Returns the function as a thunk.
    """
    return thunk.fromvalue(LazyConverter(f).converted_function)
