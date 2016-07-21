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

    /* Construct a new ``thunk`` that wraps an expression.
     *
     * Parameters
     * ----------
     * expr : any
     *     The expression to wrap.
     *
     * Returns
     * -------
     * th : any
     *     A thunk unless the expression is a strict type. */
    PyObject *(*LzThunk_FromExpr)(PyObject*);

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

extern PyTypeObject LzStrict_Type;

#define LzThunk_CheckExact(ob) (Py_TYPE(ob) == (PyTypeObject*) &LzStrict_Type)

#endif
