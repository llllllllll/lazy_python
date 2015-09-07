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


def test_L_slice():
    assert L[0, ..., 9][:5] == (0, 1, 2, 3, 4)
    assert L[0, ..., 9][5:] == (5, 6, 7, 8, 9)
    assert L[0, ..., 9][2:8] == (2, 3, 4, 5, 6, 7)
    assert L[0, ..., 9][::2] == (0, 2, 4, 6, 8)


def test_index():
    l = L[0, 1, 2]
    for n in range(3):
        assert l.index(n) == n

    with pytest.raises(ValueError):
        l.index(3)

    for n in range(1, 3):
        assert l.index(n, 1) == n

    with pytest.raises(ValueError):
        assert l.index(0, 1)

    for n in range(0, 2):
        assert l.index(n, None, 2) == n

    with pytest.raises(ValueError):
        l.index(2, None, 2)

    for n in range(5):
        with pytest.raises(ValueError):
            assert nil.index(n)


def test_count():
    l = L[1, 2, 2, 3, 3, 3]

    for n in range(4):
        assert l.count(n) == n

    for n in range(5):
        assert nil.count(n) == 0
