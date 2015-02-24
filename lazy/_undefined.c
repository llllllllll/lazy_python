#include <Python.h>

static PyObject *
undefined_strict(PyObject *self, PyObject *instance, PyObject *owner)
{
    PyErr_SetObject(owner, instance);
    return NULL;
}

PyTypeObject undefined_strict_descr = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "lazy._undefined.normalizer",               /* tp_name */
    sizeof(PyObject),                           /* tp_basicsize */
    0,                                          /* tp_itemsize */
    0,                                          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    0,                                          /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    undefined_strict,                           /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
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
    PyObject *m;
    PyObject *strict;
    PyObject *dict_;
    PyObject *undefined_inner;
    PyObject *undefined;
    PyObject *thunk;
    PyObject *thunk_fromvalue;
    int err;

    if (PyType_Ready(&undefined_strict_descr)) {
        return NULL;
    }

    if (!(dict_ = PyDict_New())) {
        return NULL;
    }

    if (!(strict = PyObject_New(PyObject, &undefined_strict_descr))) {
        Py_DECREF(dict_);
        return NULL;
    }

    err = PyDict_SetItemString(dict_, "__strict__", strict);
    Py_DECREF(strict);
    if (err) {
        Py_DECREF(dict_);
        return NULL;
    }

    undefined_inner = PyErr_NewException(
        "lazy._undefined.undefined", NULL, dict_);

    Py_DECREF(dict_);
    if (!undefined_inner) {
        return NULL;
    }

    if (!(m = PyImport_ImportModule("lazy._thunk"))) {
        Py_DECREF(undefined_inner);
        return NULL;
    }

    thunk = PyObject_GetAttrString(m, "thunk");
    Py_DECREF(m);
    if (!thunk) {
        Py_DECREF(undefined_inner);
        return NULL;
    }

    thunk_fromvalue = PyObject_GetAttrString(thunk, "fromvalue");
    Py_DECREF(thunk);
    if (!thunk_fromvalue) {
        Py_DECREF(undefined_inner);
        return NULL;
    }
    undefined = PyObject_CallFunctionObjArgs(thunk_fromvalue,
                                             undefined_inner,
                                             NULL);
    Py_DECREF(thunk_fromvalue);
    Py_DECREF(undefined_inner);
    if (!undefined) {
        return NULL;
    }

    if (!(m = PyModule_Create(&_undefined_module))) {
        return NULL;
    }

    if (PyObject_SetAttrString(m, "undefined", undefined)) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
