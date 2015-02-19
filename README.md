# `lazy` #

[![build status](https://travis-ci.org/llllllllll/lazy_python.svg?branch=master)](https://travis-ci.org/llllllllll/lazy_python)

I will write this later...


## What is lazy? ##

`lazy` is a module for making python
[lazily evaluated](http://en.wikipedia.org/wiki/Lazy_evaluation) (kinda).

`lazy` runs under python 3.5 and 3.4.


## Why lazy? ##

Why not lazy?

I think lazy computation is pretty cool, I also think python is pretty cool;
combining them is double cool.

## How to lazy? ##

There are 2 means of using lazy code:

1. `run_lazy`
1. `lazy_function`


#### `run_lazy` ####

We can convert normal python into lazy python with the `run_lazy` function
which takes a string, the 'name', globals, and locals. This is like `exec` for
lazy python. This will mutate the provided globals and locals so that we can
access the lazily evaluated code.

Example:

```python
>>> code = """
print('not lazy')
strict(print('lazy'))
"""
>>> run_lazy(code)
lazy
```


#### `lazy_function` ####

We can also use the `lazy_function` decorator. This is a hackier approach,
not that any is very good. Functions constructed with the `lazy_function`
decorator will return `thunk` objects which will be the deferred computation for
the function. Internally, things are kept lazy. Arguments will still be computed
with the strictness of the calling scope.

This means that if I call a `lazy_function` from normal python, the arguments
will be strictly evaluated before being passed into the lazy python function;
however, _all_ function calls are lazy in lazy python.

Example:

```python
@lazy_function
def f(a, b):
    return a + b
```

Calling f(1, 2) will return a `thunk` that will add 1 and 2 when it needs to be
strict. Doing anything with the returned thunk will keep chaining on more
computations until it must be strictly evaluated.


### `thunk` ###

At it's core, lazy is just a way of converting expressions into a tree of
deferred computation objects called `thunk`s. thunks wrap normal functions by
not evaluating them until the value is needed. A `thunk` wrapped function can
accept `thunk`s as arguments; this is how the tree is built.

`thunk`s represent the weak head normal form of an expression.


### `LazyTransformer` ###

While we can manually write:

```python
thunk(
    operator.add,
    thunk(lambda: 2),
    thunk(
        f,
        thunk(lambda: a),
        thunk(lambda: b),
    ),
)
```

That is dumb.

What we probably wanted to write was:

```python
2 + f(a, b)
```

To make this conversion, the `LazyTransformer` makes the needed corrections to
the abstract syntax tree of normal python.

The `LazyTransformer` will `thunk`ify all terminal `Name` nodes with a context
of `Load`, and all terminal nodes (`Int`, `Str`, `List`, etc...). This lets the
normal python runtime construct the chain of computations.


## Custom Strictness Properties ##

`strict` is actually a type that cannot be put into a `thunk`. For example:

```python
>>> type(thunk(strict, 2))
int
```

Notice that this is not a thunk, and has been strictly evaluated.

To create custom strict objects, you can subclass `strict`. This prevents the
object from getting wrapped in thunks allowing you to create strict data
structures.

Objects may also define a `__strict__` attribute that defines how to strictly
evalueate the object. For example, `undefined` can be defined as:

```python
class StrictFive(object):
    @property
    def __strict__(self):
        return 5
```

This would make `strict(StrictFive())` return 5 instead of an instance of
`StrictFive`.



## Gotchas ##


#### I opened it up in the repl, everything is strict! ####

Because the python spec says the `__repr__` of an object must return a `str`,
a call to `repr` must strictly evaluate the contents so that we can see what it
is. The repl will implicitly call `repr` on things to display them. We can see
that this is a thunk by doing:

```python
>>> a = thunk(operator.add, 2, 3)
>>> type(a)
lazy.thunk.thunk
>>> a
5
```

Again, because we need to compute something to represent it, the repl is a bad
use case for this, and might make it appear at first like this is always strict.

#### `print` didn't do anything! ####

Um, what did you think it would do?

If we write:

```python
@lazy_function
def f(a, b):
    print('printing the sum of %s and %s' % (a, b))
    return a + b
```

Then there is no reason that the print call should be executed.
No computation depends on the results, so it is casually skipped.

The solution is to force a dependency:

```python
@lazy_function
def f(a, b):
    strict(print('printing the sum of %s and %s' % (a, b)))
    return a + b
```

`strict` is a function that is used to strictly evaluate things.
Because the body of the function is interpreted as lazy python, the function
call is converted into a `thunk`, and therefore we can `strict` it.

This is true for _any_ side-effectful function call.


#### x is being evaluated strictly when I think it should be lazy ###

There are some cases where things MUST be strict based on the python language
spec. Because this is not really a new language, just an automated way of
writing really inefficient python, python's rules must be followed.

For example, `__bool__`, `__int__`, and other converters expect that the return
type must be a the proper type. This counts as a place where strictness is
needed<sup>1</sup>.

This might not be the case though, instead, I might have missed something and
you are correct, it should be lazy. If you think I missed something, open an
issue and I will try to address it as soon as possible.


#### Some stateful thing is broken ####

Sorry, you are using unmanaged state and lazy evaluation, you deserve
this. `thunks` cache the normal form so that calling strict the second time will
refer to the cached value. If this depended on some stateful function, then it
will not work as intended.


#### I tried to do x with a `thunk` and it broke! ####

The library is probably broken. This was written on a whim and I barely thought
through the use cases.

Please open an issue and I will try to get back to you as soon as possible.


### Notes ###

1. The function call for the constructor will be made lazy in the
   `LazyTransformer` (like `thunk(int, your_thunk)`), so while this is a place
   where strictness is needed, it can still be 'optimized' away.
