import pytest

from lazy import strict


def test_cannot_strict_undefined():
    from lazy import undefined

    with pytest.raises(Exception) as e:
        strict(undefined)

    assert type(e.value).__name__ == 'undefined'
