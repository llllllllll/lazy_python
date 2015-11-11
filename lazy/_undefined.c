#include <Python.h>

#include "lazy.h"

static PyObject *
undefined_strict(PyObject *self, PyObject *_)
{
    PyErr_SetObject((PyObject*) Py_TYPE(self), self);
    return NULL;
}

static PyMethodDef strict = {
    "__strict__",
    (PyCFunction) undefined_strict,
    METH_NOARGS,
    ""
};

PyDoc_STRVAR(module_doc,"An undefined value.");

static struct PyModuleDef _undefined_module = {
    PyModuleDef_HEAD_INIT,
    "lazy._undefined",
    module_doc,
    -1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__undefined(void)
{
    LzExported *lazy_symbols;
    PyObject *strict_meth = NULL;
    PyObject *undefined_inner_type = NULL;
    PyObject *undefined_inner = NULL;
    PyObject *undefined = NULL;
    PyObject *m;
    int err;

    if (!(lazy_symbols =
          PyCapsule_Import("lazy._thunk._exported_symbols", 0))) {
        return NULL;
    }

    if (!(undefined_inner_type = PyErr_NewException(
              "lazy._undefined.undefined", NULL, NULL))) {
            return NULL;
        }


    if (!(undefined_inner = PyObject_CallFunctionObjArgs(
              undefined_inner_type, NULL))) {
        goto error;
    }

    if (!(undefined = lazy_symbols->LzThunk_FromExpr(undefined_inner))) {
        goto error;
    }

    if (!(m = PyModule_Create(&_undefined_module))) {
        goto error;
    }


    if (!(strict_meth = PyCFunction_NewEx(&strict, undefined_inner, m))) {
        goto error;
    }

    err = PyObject_SetAttrString(undefined_inner_type,
                                 "__strict__",
                                 strict_meth);
    Py_DECREF(strict_meth);
    if (err) {
        goto error;
    }

    if (PyObject_SetAttrString(m, "undefined", undefined)) {
        goto error;
    }
    return m;

error:
    Py_XDECREF(strict_meth);
    Py_XDECREF(undefined_inner_type);
    Py_XDECREF(undefined_inner);
    Py_XDECREF(undefined);
    return NULL;
}
