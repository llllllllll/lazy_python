#!/usr/bin/env python
from setuptools import setup, Extension
import sys

long_description = ''

if 'upload' in sys.argv:
    with open('README.rst') as f:
        long_description = f.read()

setup(
    name='lazy_python',
    version='0.1.10',
    description='Lazy evaluation for python 3',
    author='Joe Jevnik',
    author_email='joejev@gmail.com',
    packages=[
        'lazy',
    ],
    long_description=long_description,
    license='GPL-2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Pre-processors',
    ],
    url='https://github.com/llllllllll/lazy_python',
    ext_modules=[
        Extension('lazy._undefined', ['lazy/_undefined.c']),
        Extension('lazy._thunk', ['lazy/_thunk.c']),
    ],
    install_requires=[
        'codetransformer==0.2.0',
    ],
)
