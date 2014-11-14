def strict(v):
    """
    Gets the strict value from a Thunk or concrete value.
    """
    try:
        return v.strict
    except AttributeError:
        return v


def seq(a, b):
    """
    Strictly evaluate a and return b.
    """
    strict(a)
    return b
