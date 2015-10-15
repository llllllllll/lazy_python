from lazy import data
from lazy._thunk import thunk, strict, get_children
from lazy._undefined import undefined
from lazy.bytecode import lazy_function
from lazy.include import get_include
from lazy.runtime import run_lazy
from lazy.transformer import LazyTransformer

__version__ = '0.1.11'

__all__ = [
    'LazyTransformer',
    'run_lazy',
    'lazy_function',
    'thunk',
    'data',
    'get_children',
    'get_include',
    'undefined',
    'strict',
]
