#ifndef LZ_H
#define LZ_H

#include <Python.h>

typedef struct {
    /* Construct a new ``thunk`` object or evaluate a strict type.
     *
     * Parameters
     * ----------
     * callable : callable
     *     The callable to use for this thunk
     * args : tuple
     *     The positional arguments to pass to ``callable``.
     * kwargs : dict
     *     The keyword arguments to pass to ``callable``.
     *
     * Returns
     * -------
     * th : any
     *     A thunk unless callable is the constructor for a strict type. */
    PyObject *(*LzThunk_New)(PyObject*, PyObject*, PyObject*);

    /* Construct a new ``thunk`` that wraps a single value.
     *
     * Parameters
     * ----------
     * value : any
     *     The value to wrap.
     *
     * Returns
     * -------
     * th : any
     *     A thunk unless the value is a strict type. */
    PyObject *(*LzThunk_FromValue)(PyObject*);

    /* Return the children of a thunk. These are either the (func, args, kwargs)
     * or the (normal,)
     *
     * Parameters
     * ----------
     * th : thunk
     *     The value to wrap.
     *
     * Returns
     * -------
     * children : tuple
     *     Either (func, args, kwargs) or (normal,). */
    PyObject *(*LzThunk_GetChildren)(PyObject*);
} LzExported;

#endif
