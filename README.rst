``lazy 0.2``
============

|build status|

I will write this later...

What is lazy?
-------------

``lazy`` is a module for making python `lazily
evaluated <http://en.wikipedia.org/wiki/Lazy_evaluation>`__ (kinda).

``lazy`` runs under python 3.5 and 3.4.

Why lazy?
---------

Why not lazy?

I think lazy computation is pretty cool, I also think python is pretty
cool; combining them is double cool.

How to lazy?
------------

There are 3 means of using lazy code:

1. ``lazy_function``
2. ``run_lazy``
3. IPython cell and line magics

``lazy_function``
^^^^^^^^^^^^^^^^^

``lazy_function`` takes a python function and returns a new function that is
the lazy version. This can be used as a decorator.

Example:

.. code:: python

    @lazy_function
    def f(a, b):
        return a + b

Calling ``f(1, 2)`` will return a ``thunk`` that will add 1 and 2 when it
needs to be strict. Doing anything with the returned thunk will keep
chaining on more computations until it must be strictly evaluated.

Lazy functions allow for lexical closures also:

.. code:: python

    @lazy_function
    def f(a):
        def g(b):
            return a + b
        return g

When we call ``f(1)`` we will get back a ``thunk`` like we would expect;
however, this thunk is wrapping the function ``g``. Because ``g`` was created
in a lazy context, it will also be a ``lazy_function`` implicitly. This means
that ``type(f(1)(2))`` is ``thunk``; but, ``f(1)(2) == 3``.

We can use strict to strictly evaluate parts of a lazy function, for example:

.. code:: python

    >>> @lazy_function
    ... def no_strict():
    ...    print('test')
    ...
    >>> strict(no_strict())


In this example, we never forced print, so we never saw the result of the call.
Consider this function though:

.. code:: python

    >>> @lazy_function
    ... def with_strict():
    ...    strict(print('test'))
    ...
    >>> strict(with_strict())
    test
    >>> result = with_strict()
    >>> strict(result)
    test

Here we can see how strict works inside of a lazy function. ``strict`` causes
the argument to be strictly evaluated, forcing the call to print. We can also
see that just calling ``with_strict`` is not enough to evaluate the function,
we need to force a dependency on the result.



This is implemented at the bytecode level to frontload a large part of the cost
of using the lazy machinery. There is very little overhead at function call
time as most of the overhead was spent at function creation (definiton) time.

``run_lazy``
^^^^^^^^^^^^

We can convert normal python into lazy python with the ``run_lazy`` function
which takes a string, the 'name', globals, and locals. This is like ``exec`` or
``eval`` for lazy python. This will mutate the provided globals and locals so
that we can access the lazily evaluated code.

Example:

.. code:: python

    >>> code = """
    print('not lazy')
    strict(print('lazy'))
    """
    >>> run_lazy(code)
    lazy


This also uses the same bytecode manipulation as ``lazy_function`` so they will
give the same results.


IPython cell and line magics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have IPython installed, you may use the cell and line magic machinery to
write and evaluate lazy code. For example:

.. code:: python

   In [1]: from lazy import strict

   In [2]: %lazy 2 + 2  # line magic acts as an expression
   Out[2]: 4

   In [3]: type(_2)
   Out[3]: lazy._thunk.thunk

   In [4]: %%lazy  # cell magic is treated as a statement
      ...: print('lazy')
      ...: strict(print('strict'))
      ...:
   strict



``thunk``
~~~~~~~~~

At its core, lazy is just a way of converting expressions into a tree
of deferred computation objects called ``thunk``\ s. thunks wrap normal
functions by not evaluating them until the value is needed. A ``thunk``
wrapped function can accept ``thunk``\ s as arguments; this is how the
tree is built. Some computations cannot be deferred because there is some state
that is needed to construct the thunk, or the python standard defines the
return of some method to be a specific type. These are refered to as 'strict
points'. Examples of strict points are ``str`` and ``bool`` because the python
standard says that these functions must return an instance of their own
type. Most of these converters are strict; however, some other things are
strict because it solves recursion issues in the interpreter, like accessing
``__class__`` on a thunk.


Custom Strictness Properties
----------------------------

``strict`` is actually a type that cannot be put into a ``thunk``. For
example:

.. code:: python

    >>> type(thunk(strict, 2))
    int

Notice that this is not a thunk, and has been strictly evaluated.

To create custom strict objects, you can subclass ``strict``. This
prevents the object from getting wrapped in thunks allowing you to
create strict data structures.

Objects may also define a ``__strict__`` method that defines how to
strictly evalueate the object. For example, an object could be defined
as:

.. code:: python

    class StrictFive(object):
        def __strict__(self):
            return 5

This would make ``strict(StrictFive())`` return 5 instead of an instance
of ``StrictFive``.

``undefined``
^^^^^^^^^^^^^

``undefined`` is a value that cannot be strictly evaluated. It is useful as a
placeholder for computations.

We can imagine ``undefined`` in python as:

.. code:: python

   @thunk.fromexpr
   @Exception.__new__
   class undefined(Exception):
       def __strict__(self):
           raise self

This object will raise an instance of itself when it is evaluated.
This is presented as an equivalent definition, though it is actually in c to
make nicer stack traces.

Known Issues
------------

Currently, the following things are known to not work:

Recursively defined ``thunk``\ s
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A recursively defined ``thunk`` is a thunk that appears in its own graph twice.
For example:

.. code:: python

    >>> a = thunk(lambda: a)
    >>> strict(a)

This will cause an infinite loop because in order to strictly evaluate ``a``,
we will call the function which returns ``a`` which we will try to strictly
evaluate.

Status: Bug, might fix.

This is basically correct, for example:

.. code:: python

    >>> a = lambda: a()
    >>> a()
    ...
    RuntimeError: maximum recursion depth exceeded

The difference in the thunk example is that we will drop into c code to preform
the recursion so it will not terminate in a reasonable amount of time.

The potential fix could be to try to detect these cycles and raise some
Exception; however, this might be a very expensive check in the good case
making ``thunk`` evaluation much slower.

Gotchas
-------

I opened it up in the repl, everything is strict!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because the python spec says the ``__repr__`` of an object must return a
``str``, a call to ``repr`` must strictly evaluate the contents so that
we can see what it is. The repl will implicitly call ``repr`` on things
to display them. We can see that this is a thunk by doing:

.. code:: python

    >>> a = thunk(operator.add, 2, 3)
    >>> type(a)
    lazy.thunk.thunk
    >>> a
    5

Again, because we need to compute something to represent it, the repl is
a bad use case for this, and might make it appear at first like this is
always strict.

``print`` didn't do anything!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Um, what did you think it would do?

If we write:

.. code:: python

    @lazy_function
    def f(a, b):
        print('printing the sum of %s and %s' % (a, b))
        return a + b

Then there is no reason that the print call should be executed. No
computation depends on the results, so it is casually skipped.

The solution is to force a dependency:

.. code:: python

    @lazy_function
    def f(a, b):
        strict(print('printing the sum of %s and %s' % (a, b)))
        return a + b

``strict`` is a function that is used to strictly evaluate things.
Because the body of the function is interpreted as lazy python, the
function call is converted into a ``thunk``, and therefore we can
``strict`` it.

This is true for *any* side-effectful function call.

x is being evaluated strictly when I think it should be lazy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are some cases where things MUST be strict based on the python
language spec. Because this is not really a new language, just an
automated way of writing really inefficient python, python's rules must
be followed.

For example, ``__bool__``, ``__int__``, and other converters expect that
the return type must be a the proper type. This counts as a place where
strictness is needed1.

This might not be the case though, instead, I might have missed
something and you are correct, it should be lazy. If you think I missed
something, open an issue and I will try to address it as soon as
possible.

Some stateful thing is broken
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sorry, you are using unmanaged state and lazy evaluation, you deserve
this. ``thunks`` cache the normal form so that calling strict the second
time will refer to the cached value. If this depended on some stateful
function, then it will not work as intended.

I tried to do x with a ``thunk`` and it broke!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The library is probably broken. This was written on a whim and I barely
thought through the use cases.

Please open an issue and I will try to get back to you as soon as
possible.

Notes
~~~~~

1. The function call for the constructor will be made lazy in the
   ``LazyTransformer`` (like ``thunk(int, your_thunk)``), so while this
   is a place where strictness is needed, it can still be 'optimized'
   away.

.. |build status| image:: https://travis-ci.org/llllllllll/lazy_python.svg?branch=master
   :target: https://travis-ci.org/llllllllll/lazy_python
