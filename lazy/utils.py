from uuid import uuid4


def isolate_namespace(name):
    return '_a%s%s' % (uuid4().hex, name)
