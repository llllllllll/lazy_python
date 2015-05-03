from operator import is_, not_
from types import CodeType, FunctionType

from codetransformer import CodeTransformer, Instruction, ops

from lazy._thunk import strict, thunk


def _lazy_is(a, b, *, is_=is_):
    return thunk(is_, a, b)


def _lazy_not(a, *, not_=not_):
    return thunk(not_, a)


class _lazy_function_transformer(CodeTransformer):
    """
    Transform a strict python function into a lazy function.
    """
    __name__ = 'lazy_function'

    def __call__(self, f):
        return thunk.fromvalue(
            FunctionType(
                self.visit(f.__code__),
                f.__globals__,
                f.__name__,
                tuple(map(thunk.fromvalue, f.__defaults__ or ())),
                f.__closure__,
            ),
        )

    def visit_const(self, const):
        const = super().visit_const(const)
        if not isinstance(const, CodeType):
            const = thunk.fromvalue(const)
        return const

    def visit_MAKE_FUNCTION(self, instr):
        """
        Functions should have strict names.
        """
        yield Instruction(
            ops.LOAD_CONST, self.const_index(strict)
        ).steal(instr)
        # TOS = strict
        # TOS1 = func_name

        yield Instruction(ops.ROT_TWO)
        # TOS = func_name
        # TOS1 = strict

        yield Instruction(ops.CALL_FUNCTION, 1)
        # TOS = strict(func_name)

        yield instr
        # TOS = new_function

    visit_MAKE_CLOSURE = visit_MAKE_FUNCTION

    def _visit_load_name(self, instr):
        """
        Loading a name immediatly wraps it in a `thunk`.
        """
        yield self.LOAD_CONST(thunk.fromvalue)
        # TOS = thunk.fromvalue

        yield instr
        # TOS = value
        # TOS1 = thunk.fromvalue

        yield Instruction(ops.CALL_FUNCTION, 1)
        # TOS = thunk.fromvalue(value)

    visit_LOAD_NAME = visit_LOAD_GLOBAL = visit_LOAD_FAST = _visit_load_name

    def visit_COMPARE_OP(self, instr):
        """
        Replace the `is` operator to act on the values the thunks represent.
        This makes `is` lazy.
        """
        if instr.arg != 8:  # is
            yield from self.visit_generic(instr)
            return

        yield self.LOAD_CONST(_lazy_is).steal(instr)
        # TOS = _lazy_is
        # TOS1 = a
        # TOS2 = b

        # This safe to do because `is` is commutative 100% of the time.
        # We are doing a pointer compare so we can move the operands around.
        # This saves us from doing an extra ROT_TWO to preserve the order.
        yield Instruction(ops.ROT_THREE)
        # TOS = a
        # TOS1 = b
        # TOS2 = _lazy_is

        yield Instruction(ops.CALL_FUNCTION, 2)
        # TOS = _lazy_is(b, a)

    def visit_UNARY_NOT(self, instr):
        """
        Replace the `not` operator to act on the values that the thunks
        represent.
        This makes `not` lazy.
        """
        yield self.LOAD_CONST(_lazy_not).steal(instr)
        # TOS = _lazy_not
        # TOS1 = arg

        yield Instruction(ops.ROT_TWO)
        # TOS = arg
        # TOS1 = _lazy_not

        yield Instruction(ops.CALL_FUNCTION, 1)
        # TOS = _lazy_not(arg)


lazy_function = _lazy_function_transformer()
