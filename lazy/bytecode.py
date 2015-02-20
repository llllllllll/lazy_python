from collections import OrderedDict
from dis import Bytecode, opmap
from functools import lru_cache
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
        yield _thunk_(lambda t=t: t)


def _const_convert(c, _globals=None):
    if isinstance(c, CodeType):
        return LazyConverter(c, _globals).converted_code
    else:
        return thunk(lambda c=c: c)


def id_(a):
    return a


def _default(opcode, arg):
    """
    The default opcode behavior.
    """
    yield bytes((opcode,))
    if arg is not None:
        yield arg.to_bytes(2, 'little')


class LazyConverter(object):
    class Indexer(object):
        def __init__(self, converter, key):
            self._converter = converter
            self._key = key

        @lru_cache(1)
        def __call__(self):
            return self._converter._consts.index(self._key).to_bytes(
                2, 'little',
            )

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
        self._names = OrderedDict()
        self._thunk_idx = self.Indexer(self, thunk)
        self._strict_idx = self.Indexer(self, strict)
        self._id_idx = self.Indexer(self, id_)
        self.transformations = self.LazyTransformations(self)
        self._co_names = ()
        self._globals = _globals if _globals is not None else f.__globals__
        self._call_args_idx = None
        self._call_kwargs_idx = None
        self._co_total_argcount = None

    @property
    @lru_cache(1)
    def _const_consts(self):
        return tuple(
            _const_convert(c, self._globals) for c in self.code.co_consts
        ) + (thunk, strict, id_)

    @property
    def _consts(self):
        return self._const_consts + tuple(self._names.values())

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
        self._co_names = co.co_names

        co_varnames = co.co_varnames + (
            isolate_namespace('_call_var'),
            isolate_namespace('_kwargs_var'),
        )

        len_co_varnames = len(co_varnames)
        self._call_kwargs_idx = (len_co_varnames - 1).to_bytes(2, 'little')
        self._call_args_idx = (len_co_varnames - 2).to_bytes(2, 'little')
        self._co_total_argcount = co.co_argcount + co.co_kwonlyargcount

        bc = b''.join(
            b() if isinstance(b, self.Indexer) else b
            for b in self._lazy_bytecode
        )

        return CodeType(
            co.co_argcount,
            co.co_kwonlyargcount,
            co.co_nlocals,
            co.co_stacksize + 1,
            co.co_flags,
            bc,
            self._consts,
            (),
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
        yield ops.LOAD_CONST
        yield self._strict_idx
        yield ops.ROT_TWO
        yield ops.CALL_FUNCTION
        yield b'\x01\x00'
        yield bytes((opcode,))
        yield arg.to_bytes(2, 'little')

    transform_MAKE_CLOSURE = transform_MAKE_FUNCTION

    def transform_LOAD_GLOBAL(self, opcode, arg):
        """
        There is never a `LOAD_GLOBAL` opcode in a lazy function, it looks
        up a `thunk` waiting for us the co_consts.
        """
        name = self._co_names[arg]

        def _findname(_name=name, _globals=self._globals):
            return _globals[_name]

        self._names[name] = thunk(_findname)

        yield ops.LOAD_CONST
        yield (
            len(self._const_consts) +
            list(self._names.keys()).index(name)
        ).to_bytes(2, 'little')

    transform_LOAD_NAME = transform_LOAD_GLOBAL

    def transform_LOAD_FAST(self, opcode, arg):
        if arg > self._co_total_argcount:
            yield from _default(opcode, arg)
            return

        yield ops.LOAD_CONST
        yield self._thunk_idx
        yield ops.LOAD_CONST
        yield self._id_idx
        yield ops.LOAD_FAST
        yield arg.to_bytes(2, 'little')
        yield ops.CALL_FUNCTION
        yield b'\x02\x00'


def lazy_function(f):
    """
    Creates a function whose body is lazily evaluated.
    """
    return LazyConverter(f).converted_function
