from lazy import data
from lazy._thunk import thunk, strict
from lazy._undefined import undefined
from lazy.bytecode import lazy_function
from lazy.runtime import run_lazy
from lazy.transformer import LazyTransformer

__version__ = '0.1.10'

__all__ = [
    'LazyTransformer',
    'run_lazy',
    'lazy_function',
    'thunk',
    'data',
    'undefined',
    'strict',
]
