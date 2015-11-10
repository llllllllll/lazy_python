import pytest

from lazy import thunk, strict, lazy_function, parse
from lazy.tree import Call, Normal
import lazy.operator as op


def _f(a):
    return a + 1


exprs = tuple(map(
    lazy_function, (
        lambda: 1 + 1,
        lambda: _f(1),
        lambda: _f(_f(1)),
    ),
))


@pytest.mark.parametrize('expr', exprs)
def test_compile_of_parse_identity(expr):
    assert strict(parse(expr()).lcompile()) == strict(expr())


@pytest.mark.parametrize('expr', exprs)
def test_tree_eq(expr):
    assert parse(expr()) == parse(expr())


@pytest.mark.parametrize('expr', exprs)
def test_tree_hash(expr):
    assert hash(parse(expr())) == hash(parse(expr()))


def test_tree_contains():
    tree = parse((thunk.fromexpr(1) + 2) + 3)

    assert 1 in tree
    assert 2 in tree
    assert 3 in tree
    sub = Call(Normal(op.add), (Normal(1), Normal(2)), {})
    assert sub in tree
    assert Call(Normal(op.add), (sub, Normal(3)), {}) in tree


def test_tree_subs():
    tree = parse((thunk.fromexpr(1) + 2) - 3)
    assert tree.subs({
        Call(Normal(op.add), (Normal(1), Normal(2)), {}): Normal(4)
    }) == Call(Normal(op.sub), (Normal(4), Normal(3)), {})

    other_tree = parse(thunk.fromexpr(1) + 1 + 1)
    assert other_tree.subs({1: 2}) == parse(thunk.fromexpr(2) + 2 + 2)


def test_tree_leaves():
    def f(a):
        return a

    tree = parse(thunk(f, (thunk.fromexpr(1) + 2) - 3))

    assert set(tree.leaves()) == set(map(Normal, (f, op.add, op.sub, 1, 2, 3)))
