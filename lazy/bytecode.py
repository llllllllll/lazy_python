from functools import partial
from operator import is_, not_
import sys
from types import CodeType, FunctionType

from codetransformer import CodeTransformer, Code, pattern, instructions
from codetransformer.patterns import matchany, var


from lazy._thunk import strict, thunk
from lazy.utils import instance


def _lazy_is(a, b, *, is_=is_):
    return thunk(is_, a, b)


def _lazy_not(a, *, not_=not_):
    return thunk(not_, a)


def _mk_lazy_function(thunk_type, box_functions):
    """Create a lazy_function style decorator that wraps all expressions in
    the given thunk type.

    Parameters
    ----------
    thunk_type : type
        The subclass of thunk used to box all expressions.
    box_functions : bool
        Should the top level value decorated be a thunk?

    Returns
    -------
    lazy_function : callable[callable, callable]
        The lazy_function decorator.
    """
    @instance
    class lazy_function(CodeTransformer):
        """
        Transform a strict python function into a lazy function.
        """
        __name__ = 'lazy_function'

        def __call__(self, f):
            fn = FunctionType(
                self.transform(Code.from_pycode(f.__code__)).to_pycode(),
                f.__globals__,
                f.__name__,
                tuple(map(thunk_type.fromexpr, f.__defaults__ or ())),
                f.__closure__,
            )
            if box_functions:
                fn = thunk_type.fromexpr(fn)
            return fn

        def transform_consts(self, consts):
            return tuple(
                const
                if isinstance(const, CodeType) else
                thunk_type.fromexpr(const)
                for const in super().transform_consts(consts)
            )

        @pattern(instructions.MAKE_FUNCTION | instructions.MAKE_CLOSURE)
        def _make_function(self, instr):
            """
            Functions should have strict names.
            """
            yield instructions.LOAD_CONST(strict).steal(instr)
            # TOS = strict
            # TOS1 = func_name

            yield instructions.ROT_TWO()
            # TOS = func_name
            # TOS1 = strict

            yield instructions.CALL_FUNCTION(1)
            # TOS = strict(func_name)

            yield instr
            # TOS = new_function

            yield instructions.LOAD_CONST(thunk_type.fromexpr)
            # TOS  thunk_type.fromexpr
            # TOS1 new_function

            yield instructions.ROT_TWO()
            # TOS  new_function
            # TOS1 thunk_type.fromexpr

            yield instructions.CALL_FUNCTION(1)
            # TOS  thunk_type.fromexpr(new_function)

        @pattern(
            instructions.LOAD_GLOBAL |
            instructions.LOAD_NAME |
            instructions.LOAD_DEREF,
        )
        def _load_name(self, instr):
            yield instructions.LOAD_CONST(thunk_type.fromexpr).steal(instr)
            # TOS  thunk_type.fromexpr

            yield instr
            # TOS  v
            # TOS1 thunk_type.fromexpr

            yield instructions.CALL_FUNCTION(1)
            # TOS thunk_type.fromexpr(v)

        @pattern(instructions.LOAD_FAST)
        def _load_fast(self, instr):
            name = instr.arg
            if name in self.code.argnames:
                # perf note: we only need to wrap lookups to arguments as
                # thunks To assign to a name, it must have been a value already
                # so it is a thunk_type unless it was passed into the function.
                yield instructions.LOAD_CONST(thunk_type.fromexpr).steal(instr)
                # TOS  thunk_type.fromexpr

                yield instr
                # TOS  v
                # TOS  thunk_type.fromexpr

                yield instructions.CALL_FUNCTION(1)
                # TOS  thunk_type.fromexpr(v)
            else:
                yield instr
                # TOS  v

        @pattern(instructions.COMPARE_OP)
        def _compare_op(self, instr):
            """
            Replace the `is` operator to act on the values the thunk represent.
            This makes `is` lazy.
            """
            if instr.arg != 8:  # is
                yield instr
                return

            yield instructions.LOAD_CONST(_lazy_is).steal(instr)
            # TOS  = _lazy_is
            # TOS1 = a
            # TOS2 = b

            # This safe to do because `is` is commutative 100% of the time.
            # We are doing a pointer compare so we can move the operands
            # around. This saves us from doing an extra ROT_TWO to preserve the
            # order.
            yield instructions.ROT_THREE()
            # TOS  = a
            # TOS1 = b
            # TOS2 = _lazy_is

            yield instructions.CALL_FUNCTION(2)
            # TOS = _lazy_is(b, a)

        @pattern(instructions.UNARY_NOT)
        def _unary_not(self, instr):
            """
            Replace the `not` operator to act on the values that the thunks.
            represent.
            This makes `not` lazy.
            """
            yield instructions.LOAD_CONST(_lazy_not).steal(instr)
            # TOS  = _lazy_not
            # TOS1 = arg

            yield instructions.ROT_TWO()
            # TOS  = arg
            # TOS1 = _lazy_not

            yield instructions.CALL_FUNCTION(1)
            # TOS = _lazy_not(arg)

        @pattern(
            instructions.BUILD_MAP,
            matchany[var],
            instructions.MAP_ADD,
            matchany[var],
            instructions.JUMP_ABSOLUTE,
            instructions.RETURN_VALUE,
        )
        def _start_dict_comprehension(self, instr, *instrs):
            # put thunk call on the stack for right befor the return.
            yield instructions.LOAD_CONST(partial(thunk_type, dict))
            # TOS  partial(thunk_type, dict)

            yield instr
            # TOS  dict_
            # TOS1 partial(thunk_type, dict)

            *body, ret = instrs
            yield from self.patterndispatcher(body)
            # TOS  dict_
            # TOS1 partial(thunk_type, dict)

            yield ret

        def _non_dict_comprehension(build_instr, append_instr, type_):
            @pattern(
                build_instr,
                matchany[var],
                append_instr,
                matchany[var],
                instructions.RETURN_VALUE,
            )
            def comprehension(self, *instrs):
                first, *body, ret = instrs

                yield instructions.LOAD_CONST(partial(thunk_type, type_))
                # TOS  partial(thunk_type, type_)

                yield first
                # TOS  strict_seq
                # TOS1 partial(thunk_type, type_)

                yield from self.patterndispatcher(body)
                # TOS  strict_seq
                # TOS1 partial(thunk_type, type_)

                yield instructions.CALL_FUNCTION(1)
                # TOS  partial(thunk_type, type_)(*strict_seq)

                yield ret

            return comprehension

        _list_comprehensions = _non_dict_comprehension(
            instructions.BUILD_LIST,
            instructions.LIST_APPEND,
            list,
        )
        _set_comprehensions = _non_dict_comprehension(
            instructions.BUILD_SET,
            instructions.SET_ADD,
            set,
        )

        del _non_dict_comprehension

        if hasattr(instructions, 'STORE_MAP'):
            # Python 3.4

            @pattern(instructions.BUILD_MAP)
            def _build_map(self, instr):
                yield instructions.LOAD_CONST(thunk_type(dict)).steal(instr)
                # TOS  = m = thunk_type(dict)

                yield from (instructions.DUP_TOP(),) * instr.arg
                # TOS  = m
                # ...
                # TOS[instr.arg] = m

            @pattern(instructions.STORE_MAP)
            def _store_map(self, instr):
                # TOS  = k
                # TOS1 = v
                # TOS2 = m
                # TOS3 = m

                yield instructions.ROT_THREE().steal(instr)
                # TOS  = v
                # TOS1 = m
                # TOS2 = k
                # TOS3 = m

                yield instructions.ROT_THREE()
                # TOS  = m
                # TOS1 = k
                # TOS2 = v
                # TOS3 = m

                yield instructions.ROT_TWO()
                # TOS  = k
                # TOS1 = m
                # TOS2 = v
                # TOS3 = m

                yield instructions.STORE_SUBSCR()
                # TOS  = m

        else:
            # Python 3.5 and beyond!

            @pattern(instructions.BUILD_MAP)
            def _build_map(self, instr):
                # TOS  k_0
                # TOS1 v_0
                # ...
                # TOSn k_n
                # TOSm v_n

                yield instr
                # TOS  dict_

                yield instructions.LOAD_CONST(
                    partial(thunk_type, dict),
                )
                # TOS  partial(thunk_type, dict)
                # TOS1 dict_

                yield instructions.ROT_TWO()
                # TOS  dict_
                # TOS1 partial(thunk_type, dict)

                yield instructions.CALL_FUNCTION_KW(0)
                # TOS  partial(thunk_type, dict)(**dict_)

        def _build_seq(build_instr, type_):
            @pattern(build_instr)
            def build_seq(self, instr):
                # TOS  v_0
                # ...
                # TOSn v_n

                yield instructions.BUILD_TUPLE(instr.arg).steal(instr)
                # TOS  (v_0, ..., v_n)

                yield instructions.LOAD_CONST(partial(thunk_type, type_))
                # TOS  partial(thunk_type, type_)
                # TOS1 (v_0, ..., v_n)

                yield instructions.ROT_TWO()
                # TOS  (v_0, ..., v_n)
                # TOS1 partial(thunk_type, type_)

                yield instructions.CALL_FUNCTION(1)
                # TOS  partial(thunk_type, type_)(v_0, ..., v_n)

            return build_seq

        _build_tuple = _build_seq(instructions.BUILD_TUPLE, tuple)
        _build_list = _build_seq(instructions.BUILD_LIST, list)
        _build_set = _build_seq(instructions.BUILD_SET, set)

        del _build_seq

        @staticmethod
        def _import_wrapper(level, fromlist, name, *, _getframe=sys._getframe):
            calling_frame = _getframe(1)
            return thunk_type(
                __import__,
                name,
                calling_frame.f_globals,
                calling_frame.f_locals,
                fromlist,
                level,
            )

        @pattern(instructions.IMPORT_NAME)
        def _import_name(self, instr):
            # TOS  fromlist
            # TOS1 level

            yield instructions.LOAD_CONST(self._import_wrapper).steal(instr)
            # TOS  self._import_wrapper
            # TOS1 fromlist
            # TOS2 level

            yield instructions.ROT_THREE()
            # TOS  fromlist
            # TOS1 level
            # TOS2 self._import_wrapper

            yield instructions.LOAD_CONST(instr.arg)
            # TOS  name
            # TOS1 fromlist
            # TOS2 level
            # TOS3 self._import_wrapper

            yield instructions.CALL_FUNCTION(3)
            # TOS  self._import_wrapper(level, fromlist, name)

    return lazy_function


lazy_function = _mk_lazy_function(thunk, True)
