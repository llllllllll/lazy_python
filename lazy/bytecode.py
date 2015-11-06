from operator import is_, not_
import sys
from types import CodeType, FunctionType

from codetransformer import CodeTransformer, Code, pattern, instructions
from codetransformer.patterns import matchany, var, DEFAULT_STARTCODE


from lazy._thunk import strict, thunk
from lazy.utils import instance


def _lazy_is(a, b, *, is_=is_):
    return thunk(is_, a, b)


def _lazy_not(a, *, not_=not_):
    return thunk(not_, a)


IN_COMPREHENSION = 'IN_COMPREHENSION'
all_startcodes = DEFAULT_STARTCODE, IN_COMPREHENSION


@instance
class lazy_function(CodeTransformer):
    """
    Transform a strict python function into a lazy function.
    """
    __name__ = 'lazy_function'

    def __call__(self, f):
        return thunk.fromvalue(
            FunctionType(
                self.transform(Code.from_pycode(f.__code__)).to_pycode(),
                f.__globals__,
                f.__name__,
                tuple(map(thunk.fromvalue, f.__defaults__ or ())),
                f.__closure__,
            ),
        )

    def transform_consts(self, consts):
        return tuple(
            const if isinstance(const, CodeType) else thunk.fromvalue(const)
            for const in super().transform_consts(consts)
        )

    @pattern(
        instructions.MAKE_FUNCTION | instructions.MAKE_CLOSURE,
        startcodes=all_startcodes,
    )
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

        yield instructions.LOAD_CONST(thunk.fromvalue)
        # TOS  thunk.fromvalue
        # TOS1 new_function

        yield instructions.ROT_TWO()
        # TOS  new_function
        # TOS1 thunk.fromvalue

        yield instructions.CALL_FUNCTION(1)
        # TOS  thunk.fromvalue(new_function)

    @pattern(
        instructions.LOAD_GLOBAL |
        instructions.LOAD_NAME |
        instructions.LOAD_DEREF,
        startcodes=all_startcodes,
    )
    def _load_name(self, instr):
        yield instructions.LOAD_CONST(thunk.fromvalue).steal(instr)
        # TOS  thunk.fromvalue

        yield instr
        # TOS  v
        # TOS1 thunk.fromvalue

        yield instructions.CALL_FUNCTION(1)
        # TOS thunk.fromvalue(v)

    @pattern(instructions.LOAD_FAST, startcodes=all_startcodes)
    def _load_fast(self, instr):
        name = instr.arg
        if name in self.code.argnames:
            # perf note: we only need to wrap lookups to arguments as thunks.
            # To assign to a name, it must have been a value already so it
            # is a thunk unless it was passed into the function.
            yield instructions.LOAD_CONST(thunk.fromvalue).steal(instr)
            # TOS  thunk.fromvalue

            yield instr
            # TOS  v
            # TOS  thunk.fromvalue

            yield instructions.CALL_FUNCTION(1)
            # TOS  thunk.fromvalue(v)
        else:
            yield instr
            # TOS  v

    @pattern(instructions.COMPARE_OP, startcodes=all_startcodes)
    def _compare_op(self, instr):
        """
        Replace the `is` operator to act on the values the thunks represent.
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
        # We are doing a pointer compare so we can move the operands around.
        # This saves us from doing an extra ROT_TWO to preserve the order.
        yield instructions.ROT_THREE()
        # TOS  = a
        # TOS1 = b
        # TOS2 = _lazy_is

        yield instructions.CALL_FUNCTION(2)
        # TOS = _lazy_is(b, a)

    @pattern(instructions.UNARY_NOT, startcodes=all_startcodes)
    def _unary_not(self, instr):
        """
        Replace the `not` operator to act on the values that the thunks
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

    @pattern(instructions.BUILD_MAP, matchany[var], instructions.MAP_ADD)
    def _start_dict_comprehension(self, instr, *instrs):
        yield instructions.LOAD_CONST(thunk(dict)).steal(instr)
        # TOS  = thunk(dict)

        yield instructions.STORE_FAST('__comp_accumulator__')

        *body, map_add = instrs
        yield from self.patterndispatcher(body)
        # TOS  = k
        # TOS1 = v

        yield instructions.LOAD_FAST('__comp_accumulator__').steal(map_add)
        # TOS  = __map__
        # TOS1 = k
        # TOS2 = v

        yield instructions.ROT_TWO()
        # TOS  = k
        # TOS1 = __map__
        # TOS2 = v

        yield instructions.STORE_SUBSCR()
        self.begin(IN_COMPREHENSION)

    def _non_dict_comprehension(self, *instrs):
        first, *body, ret = instrs
        yield first
        yield from self.patterndispatcher(body)
        # TOS  seq

        yield instructions.LOAD_CONST(thunk.fromvalue)
        # TOS  thunk.fromvalue
        # TOS1 seq

        yield instructions.ROT_TWO()
        # TOS  seq
        # TOS1 thunk.fromvalue

        yield instructions.CALL_FUNCTION(1)
        # TOS  thunk.fromvalue(seq)

        yield ret

    _set_comprehensions = pattern(
        instructions.BUILD_SET,
        matchany[var],
        instructions.SET_ADD,
        matchany[var],
        instructions.RETURN_VALUE,
        startcodes=all_startcodes,
    )(_non_dict_comprehension)
    _list_comprehensions = pattern(
        instructions.BUILD_LIST,
        matchany[var],
        instructions.LIST_APPEND,
        matchany[var],
        instructions.RETURN_VALUE,
        startcodes=all_startcodes,
    )(_non_dict_comprehension)

    @pattern(instructions.RETURN_VALUE, startcodes=(IN_COMPREHENSION,))
    def _return_value_from_comprehension(self, instr):
        yield instructions.LOAD_FAST('__comp_accumulator__').steal(instr)
        # TOS  = __map__

        yield instr

    if hasattr(instructions, 'STORE_MAP'):
        # Python 3.4

        @pattern(instructions.BUILD_MAP)
        def _build_map(self, instr):
            yield instructions.LOAD_CONST(thunk(dict)).steal(instr)
            # TOS  = m = thunk(dict)

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
            yield instr
            # TOS  dict_

            yield instructions.LOAD_CONST(thunk.fromvalue)
            # TOS  thunk.fromvalue
            # TOS1 dict_

            yield instructions.ROT_TWO()
            # TOS  dict_
            # TOS1 thunk.fromvalue

            yield instructions.CALL_FUNCTION(1)
            # TOS  thunk.fromvalue(dict_)

    @pattern(instructions.BUILD_SET, startcodes=all_startcodes)
    def _build_set(self, instr):
        # TOS  v_0
        # ...
        # TOSn v_n

        yield instructions.BUILD_TUPLE(instr.arg).steal(instr)
        # TOS  (v_0, ..., v_n)

        yield instructions.LOAD_CONST(thunk.fromvalue(set))
        # TOS  thunk.fromvalue(set)
        # TOS1 (v_0, ..., v_n)

        yield instructions.ROT_TWO()
        # TOS  (v_0, ..., v_n)
        # TOS1 thunk.fromvalue(set)

        yield instructions.CALL_FUNCTION(1)
        # TOS  thunk.fromvalue(set)((v_0, ..., v_n))

    @pattern(instructions.BUILD_LIST, startcodes=all_startcodes)
    def _build_list(self, instr):
        # TOS  v_0
        # ...
        # TOSn v_n

        yield instr
        # TOS  [v_0, ..., v_n]

        yield instructions.LOAD_CONST(thunk.fromvalue)
        # TOS  thunk.fromvalue
        # TOS1 [v_0, ..., v_n]

        yield instructions.ROT_TWO()
        # TOS  [v_0, ..., v_n]
        # TOS1 thunk.fromvalue

        yield instructions.CALL_FUNCTION(1)
        # TOS  thunk.fromvalue([v_0, ..., v_n])

    @staticmethod
    def _import_wrapper(level, fromlist, name, *, _getframe=sys._getframe):
        calling_frame = _getframe(1)
        return thunk(
            __import__,
            name,
            calling_frame.f_globals,
            calling_frame.f_locals,
            fromlist,
            level,
        )

    @pattern(instructions.IMPORT_NAME, startcodes=all_startcodes)
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
