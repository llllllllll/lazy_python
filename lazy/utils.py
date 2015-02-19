from uuid import uuid4


def safesetattr(obj, attr, value):
    """
    Because we are overriding __setattr__, we need a
    non-recursive way of setting attributes.

    This is to be used to set attributes internally.
    """
    object.__setattr__(obj, attr, value)


def safegetattr(obj, name, *default):
    """
    Because we are overridding __getattr__, we need a
    non-recursive way of getting attributes.

    This is used to get attributes internally.
    """
    return object.__getattribute__(obj, name, *default)


def isolate_namespace(name):
    return '_a%s%s' % (uuid4().hex, name)


def is_dunder(name):
    return name.startswith('__') and name.endswith('__')


def singleton(cls):
    """
    Class decorator for creating singletons.
    """
    cls._instance = None
    old_new = cls.__new__

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            if cls.__new__ is not object.__new__:
                cls._instance = old_new(cls)
            else:
                cls._instance = old_new(cls, *args, **kwargs)

        return cls._instance

    cls.__new__ = __new__
    return cls
