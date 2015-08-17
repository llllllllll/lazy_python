from lazy.utils import isolate_namespace


def test_isolate_namespace():
    assert 'test' != isolate_namespace('test')
