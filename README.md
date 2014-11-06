# `lazy` #

I will write this later...


## What is lazy? ##

`lazy` is a module for making python
[lazily evaluated](http://en.wikipedia.org/wiki/Lazy_evaluation) (kinda).


## Why lazy? ##

Why not lazy?

I think lazy computation is pretty cool, I also think python is pretty cool;
combining them is double cool.

## How to lazy? ##

You can convert normal python into lazy python with the `run_lazy` function
which takes a string, the 'name', globals, and locals. This is like `exec` for
lazy python.

You can also use the `lazy_function` decorator. This is the hackier approach,
not that either is very good. Functions constructed with the `lazy_function`
decorator will return `Thunk` objects which will be the deferred computation for
the function, internally, things are kept lazy. Arguments will still be computed
with the strictness of the calling scope.

This means that if I call a `lazy_function` from normal python, the arguments
will be strictly evaluated before being passed into the lazy python function;
however, _all_ function calls are lazy in lazy python.


### `Thunk` ###

At it's core, lazy is just a way of converting expressions into a tree of
deferred computation objects called `Thunk`s. Thunks wrap normal functions by
not evaluating them until the value is needed. A `Thunk` wrapped functions can
accept `Thunk`s as arguments; this is how the tree is built.


### `LazyTransformer` ###

While I can manually write:

```python
Thunk(operator.add, Thunk(lambda: 2), Thunk(f, a, b))
```

that is dumb.

What I probably wanted to write was:

```python
2 + f(a, b)
```

To make this conversion, the `LazyTransformer` makes the needed corrections to
the abstract syntax tree of normal python.


## Gotchas ##


#### I opened it up in the repl, everything is strict! ####

Because the python spec says the `__repr__` of an object must return a `str`,
a call to `repr` must strictly evaluate the contents so that we can see what it
is. The repl will implicitly call `repr` on things to display them. You can see
that this is a thunk by doing:

```python
>>> a = Thunk(operator.add, 2, 3)
>>> type(a)
lazy.thunk.Thunk
>>> a
5
```

Again, because we need to compute something to represent it, the repl is a bad
use case for this, and might make it appear at first like this is always strict.

#### `print` didn't do anything! ####

Um, what did you think it would do?

If you write:

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
    print('printing the sum of %s and %s' % (a, b)).strict
    return a + b
```

`strict` is a property of a `Thunk` that forces the value (and caches it).
Because the body of the function is interpreted as lazy python, the function
call is converted into a `Thunk`, and therefore you can `strict` it.

This is true for _any_ side-effectful function call.


#### x is being evaluated strictly when I think it should be lazy ###

There are some cases where things MUST be strict based on the python language
spec. Because this is not really a new language, just an automated way of
writing really inefficient python, python's rules must be followed.

For example, `__bool__`, `__int__`, and other converters expect that the return
type MUST be a the proper type. This counts as a place where strictness is
needed for this reason<sup>1</sup>.

This might not be the case though, instead, I might have missed something and
you are correct, it should be lazy. If you think this is the case, open an
issue and I will try to address it as soon as possible.


#### I tried to do x with a `Thunk` and it broke! ####

The library is probably broken. This was written on a whim and I barely thought
through the use cases.

Please open an issue and I will try to get back to you as soon as possible.


### Notes ###

1. The function call for the constructor will be made lazy in the
   `LazyTransformer` (like `Thunk(int, your_thunk)`), so while this is a place
   where strictness is needed, it can still be optimized away.
