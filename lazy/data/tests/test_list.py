import pytest

from lazy.data import L, nil, Cons


def test_lazy_index():
    ls = Cons(None, Cons(2, Cons(None, nil)))
    assert ls[1] is 2


def test_L_abstract():
    with pytest.raises(TypeError):
        L()


def test_iter():
    for e, v in enumerate(Cons(0, Cons(1, Cons(2, Cons(3, nil))))):
        assert e == v


def test_L_itemconstructor():
    assert L[0, 1, 2] == (0, 1, 2)


def test_L_range():
    assert L[0, ..., 5] == (0, 1, 2, 3, 4, 5)
    assert L[0, ..., 6, 2] == (0, 2, 4, 6)
