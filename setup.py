#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='lazy',
    version='0.1.0',
    description='Lazy evaluation for python',
    author='Joe Jevnik',
    author_email='joejev@gmail.com',
    packages=find_packages(),
    long_description=long_description,
    license='GPL-2',
    classifiers=[
        'Development Status :: 3 - Alpha'
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Pre-processors',
    ],
    install_requires=[
        'six',
    ],
    url="https://github.com/llllllllll/lazy_python"
)
