#include <Python.h>
#include <stdbool.h>

// We can only use matmul on 3.5+.
#define NT_HAS_MATMUL PY_MINOR_VERSION >= 5

typedef struct{
    PyObject_HEAD
    void *wr_func;
}callablewrapper;

/* Binary  wrapper --------------------------------------------------------- */

static PyTypeObject binwrapper_type;

static PyObject *
binwrapper_call(callablewrapper *self, PyObject *args, PyObject *kwargs)
{
    if (kwargs) {
        PyErr_SetString(PyExc_TypeError,
                        "callable does not accept keyword arguments");
        return NULL;
    }

    if (PyTuple_GET_SIZE(args) != 2) {
        PyErr_Format(PyExc_TypeError,
                     "callable expects 2 arguments, passed %zd",
                     PyTuple_GET_SIZE(args));
        return NULL;
    }

    return ((PyObject *(*)(PyObject*,PyObject*)) self->wr_func)(
        PyTuple_GET_ITEM(args, 0),
        PyTuple_GET_ITEM(args, 1));
}

PyDoc_STRVAR(callablewrapper_doc, "A wrapper for a c functions.");

static PyTypeObject binwrapper_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "lazy._thunk.binwrapper",                   /* tp_name */
    sizeof(callablewrapper),                    /* tp_basicsize */
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
    (ternaryfunc) binwrapper_call,              /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    callablewrapper_doc,                        /* tp_doc */
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
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
};

static PyObject *
binwrapper_from_func(void *func)
{
    callablewrapper *wr;

    if (!(wr = PyObject_New(callablewrapper, &binwrapper_type))) {
        return NULL;
    }
    ((PyObject*) wr)->ob_type = &binwrapper_type;
    wr->wr_func = func;
    return (PyObject*) wr;
}

/* Unary wrapper ----------------------------------------------------------- */

static PyTypeObject unarywrapper_type;

static PyObject *
unarywrapper_call(callablewrapper *self, PyObject *args, PyObject *kwargs)
{
    if (kwargs) {
        PyErr_SetString(PyExc_TypeError,
                        "callable does not accept keyword arguments");
        return NULL;
    }

    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_Format(PyExc_TypeError,
                     "callable expects 1 argument, passed %zd",
                     PyTuple_GET_SIZE(args));
        return NULL;
    }

    return ((PyObject *(*)(PyObject*)) self->wr_func)(
        PyTuple_GET_ITEM(args, 0));
}

static PyTypeObject unarywrapper_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "lazy._thunk.unarywrapper",                 /* tp_name */
    sizeof(callablewrapper),                    /* tp_basicsize */
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
    (ternaryfunc) unarywrapper_call,            /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    callablewrapper_doc,                        /* tp_doc */
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
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
};

static PyObject *
unarywrapper_from_func(void *func)
{
    callablewrapper *wr;

    if (!(wr = (callablewrapper*) PyType_GenericAlloc(&unarywrapper_type,
                                                      0))) {
        return NULL;
    }
    ((PyObject*) wr)->ob_type = &unarywrapper_type;
    wr->wr_func = func;
    return (PyObject*) wr;
}

/* Ternary wrapper --------------------------------------------------------- */

static PyTypeObject ternarywrapper_type;

static PyObject *
ternarywrapper_call(callablewrapper *self, PyObject *args, PyObject *kwargs)
{
    if (kwargs) {
        PyErr_SetString(PyExc_TypeError,
                        "callable does not accept keyword arguments");
        return NULL;
    }

    if (PyTuple_GET_SIZE(args) != 3) {
        PyErr_Format(PyExc_TypeError,
                     "callable expects 3 arguments, passed %zd",
                     PyTuple_GET_SIZE(args));
        return NULL;
    }

    return ((PyObject *(*)(PyObject*, PyObject*, PyObject*)) self->wr_func)(
        PyTuple_GET_ITEM(args, 0),
        PyTuple_GET_ITEM(args, 1),
        PyTuple_GET_ITEM(args, 2));
}

static PyTypeObject ternarywrapper_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "lazy._thunk.ternarywrapper",               /* tp_name */
    sizeof(callablewrapper),                    /* tp_basicsize */
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
    (ternaryfunc) ternarywrapper_call,          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    callablewrapper_doc,                        /* tp_doc */
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
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
};

static PyObject *
ternarywrapper_from_func(void *func)
{
    callablewrapper *wr;

    if (!(wr = (callablewrapper*) PyType_GenericAlloc(&ternarywrapper_type,
                                                      0))) {
        return NULL;
    }
    ((PyObject*) wr)->ob_type = &ternarywrapper_type;
    wr->wr_func = func;
    return (PyObject*) wr;
}

/* thunk ------------------------------------------------------------------- */

typedef struct{
    PyObject_HEAD
    PyObject *th_func;
    PyObject *th_args;
    PyObject *th_kwargs;
    PyObject *th_normal;
}thunk;

static PyTypeObject thunk_type;

/* strict ------------------------------------------------------------------- */

static PyObject *strict_eval(PyObject*);

/* Strictly evaluate a thunk.
   return: A borrowed reference. */
static PyObject *
_strict_eval_borrowed(PyObject *self)
{
    PyObject *normal_func;
    PyObject *normal_args;
    PyObject *normal_kwargs;
    Py_ssize_t nargs;
    Py_ssize_t n;
    PyObject *arg;
    PyObject *key;
    PyObject *value;

    if (!((thunk*) self)->th_normal) {
        if (!(normal_func = strict_eval(((thunk*) self)->th_func))) {
            return NULL;
        }

        nargs = PyTuple_GET_SIZE(((thunk*) self)->th_args);
        if (!(normal_args = PyTuple_New(nargs))) {
            Py_DECREF(normal_func);
            return NULL;
        }

        for (n = 0;n < nargs;++n) {
            if (!(arg = strict_eval(
                      PyTuple_GET_ITEM(((thunk*) self)->th_args, n)))) {
                Py_DECREF(normal_func);
                Py_DECREF(normal_args);
                return NULL;
            }
            PyTuple_SET_ITEM(normal_args, n, arg);
        }

        if (((thunk*) self)->th_kwargs) {
            if (!(normal_kwargs = PyDict_Copy(((thunk*) self)->th_kwargs))) {
                Py_DECREF(normal_func);
                Py_DECREF(normal_args);
                return NULL;
            }

            n = 0;
            while (PyDict_Next(normal_args, &n, &key, &value)) {
                if ((!(arg = strict_eval(value))) ||
                    PyDict_SetItem(normal_args, key, arg)) {

                    Py_DECREF(normal_func);
                    Py_DECREF(normal_args);
                    Py_DECREF(normal_kwargs);
                    return NULL;
                }
            }
        }
        else {
            normal_kwargs = NULL;
        }

        ((thunk*) self)->th_normal = PyObject_Call(normal_func,
                                                   normal_args,
                                                   normal_kwargs);
        Py_DECREF(normal_func);
        Py_DECREF(normal_args);
        Py_XDECREF(normal_kwargs);
        if (!((thunk*) self)->th_normal) {
            return NULL;
        }
        /* Remove the references to the function and args to not persist
           these references. */
        Py_CLEAR(((thunk*) self)->th_func);
        Py_CLEAR(((thunk*) self)->th_args);
        Py_CLEAR(((thunk*) self)->th_kwargs);
    }

    return ((thunk*) self)->th_normal;
}

static PyTypeObject strict_type;

/* Strictly evaluate a thunk.
   return: A new reference. */
static PyObject *
strict_eval(PyObject *th)
{
    PyObject *normal;

    if (PyObject_IsInstance(th, (PyObject*)  &thunk_type)) {
        if (!(normal = _strict_eval_borrowed(th))) {
            return NULL;
        }
    }
    else if (!(normal = PyObject_GetAttrString(th, "__strict__"))) {
        if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
            PyErr_Clear();
            normal = th;
        }
        else {
            return NULL;
        }
    }

    Py_INCREF(normal);
    return normal;
}

static PyObject *
strict_new(PyObject *cls, PyObject *args, PyObject *kwargs)
{
    static const char * const keywords[] = {"expr", NULL};
    PyObject *th;

    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "O:strict",
                                     (char**) keywords,
                                     &th)) {
        return NULL;
    }

    return strict_eval(th);
}

PyDoc_STRVAR(strict_doc, "A strict computation.");

static PyTypeObject strict_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "lazy._thunk.strict",                       /* tp_name */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    strict_doc,                                 /* tp_doc */
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
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    (newfunc) strict_new,                       /* tp_new */
};

/* Thunk methods ----------------------------------------------------------- */

static void
thunk_free(thunk *self)
{
  PyObject_GC_Del(self);
}

static void
thunk_dealloc(thunk *self)
{
    Py_XDECREF(self->th_func);
    Py_XDECREF(self->th_args);
    Py_XDECREF(self->th_kwargs);
    Py_XDECREF(self->th_normal);
    Py_TYPE(self)->tp_free((PyObject*) self);
}

static PyObject *
thunk_alloc(PyTypeObject *cls, Py_ssize_t nitems)
{
    return PyObject_GC_New(PyObject, cls);
}


/* Create a thunk without checking if `func` is a strict type.
   return: A new reference. */
static PyObject *
_thunk_new_no_check(PyTypeObject *cls,
                    PyObject *func,
                    PyObject *args,
                    PyObject *kwargs)
{
    thunk *self;

    if (!(self = (thunk*) cls->tp_alloc(cls, 0))) {
        return NULL;
    }

    Py_INCREF(func);
    self->th_func = func;
    Py_INCREF(args);
    self->th_args = args;
    Py_XINCREF(kwargs);
    self->th_kwargs = kwargs;
    self->th_normal = NULL;
    return (PyObject*) self;
}

/* Create a thunk OR construct a strict type.
   return: A new reference. */
static PyObject *
thunk_new(PyObject *cls, PyObject *args, PyObject *kwargs)
{
    PyObject *th_func;
    PyObject *th_args = NULL;
    Py_ssize_t nargs;
    Py_ssize_t n;
    PyObject *tmp;
    PyObject *ret;

    nargs = PyTuple_GET_SIZE(args);
    if (nargs < 1) {
        PyErr_SetString(PyExc_TypeError, "Missing callable argument");
        return NULL;
    }

    th_func = PyTuple_GET_ITEM(args, 0);

    if (!PyCallable_Check(th_func)) {
        PyErr_SetString(PyExc_ValueError, "func must be callable");
        return NULL;
    }

    if (!(th_args = PyTuple_New(nargs - 1))) {
        return NULL;
    }

    for (n = 0;n < nargs - 1;++n) {
        tmp = PyTuple_GET_ITEM(args, n + 1);
        Py_INCREF(tmp);
        PyTuple_SET_ITEM(th_args, n, tmp);
    }

    if (PyObject_IsInstance(th_func, (PyObject*) &PyType_Type) &&
        PyObject_IsSubclass(th_func, (PyObject*) &strict_type)) {
        /* Strict types get evaluated strictly. */
        if (PyTuple_GET_SIZE(th_args)) {
            /* There are args to apply to strict. */
            ret = PyObject_Call(th_func, th_args, kwargs);
        }
        else {
            /* There are no args to apply, return the strict type. */
            Py_INCREF(th_func);
            ret = th_func;
        }
    }
    else {
        ret = _thunk_new_no_check((PyTypeObject*) cls,
                                  th_func,
                                  th_args,
                                  kwargs);
    }

    Py_DECREF(th_args);

    return ret;
}


/* Binary operators --------------------------------------------------------- */
#define THUNK_BINOP(name, func)                                         \
    static PyObject *                                                   \
    name(PyObject *a, PyObject *b)                                      \
    {                                                                   \
        PyObject *fn;                                                   \
        PyObject *arg;                                                  \
        PyObject *ret;                                                  \
        int instance_p;                                                 \
        if (!(fn = binwrapper_from_func(func))) {                       \
            return NULL;                                                \
        }                                                               \
        if (!(arg = PyTuple_Pack(2, a, b))) {                           \
            Py_DECREF(fn);                                              \
        }                                                               \
        instance_p = PyObject_IsInstance(a, (PyObject*) &thunk_type);   \
        if (instance_p == -1) {                                         \
            Py_DECREF(arg);                                             \
            Py_DECREF(fn);                                              \
            return NULL;                                                \
        }                                                               \
        ret = _thunk_new_no_check(Py_TYPE(instance_p ? a : b),          \
                                  fn,                                   \
                                  arg,                                  \
                                  NULL);                                \
        Py_DECREF(fn);                                                  \
        Py_DECREF(arg);                                                 \
        return ret;                                                     \
    }

THUNK_BINOP(thunk_add, PyNumber_Add)
THUNK_BINOP(thunk_sub, PyNumber_Subtract)
THUNK_BINOP(thunk_mul, PyNumber_Multiply)

#if NT_HAS_MATMUL
THUNK_BINOP(thunk_matmul, PyNumber_MatrixMultiply)
#endif

THUNK_BINOP(thunk_floordiv, PyNumber_FloorDivide)
THUNK_BINOP(thunk_truediv, PyNumber_TrueDivide)
THUNK_BINOP(thunk_rem, PyNumber_Remainder)
THUNK_BINOP(thunk_divmod, PyNumber_Divmod)
THUNK_BINOP(thunk_lshift, PyNumber_Lshift)
THUNK_BINOP(thunk_rshift, PyNumber_Rshift)
THUNK_BINOP(thunk_and, PyNumber_And)
THUNK_BINOP(thunk_xor, PyNumber_Xor)
THUNK_BINOP(thunk_or, PyNumber_Or)

/* Inplace operators -------------------------------------------------------- */

#define THUNK_INPLACE(name, func)                               \
    static PyObject *                                           \
    name(PyObject *self, PyObject *other)                       \
    {                                                           \
        PyObject *val;                                          \
        if (!(val = _strict_eval_borrowed(self))) {             \
            return NULL;                                        \
        }                                                       \
        return func(val, other);                                \
    }

THUNK_INPLACE(thunk_iadd, PyNumber_InPlaceAdd)
THUNK_INPLACE(thunk_isub, PyNumber_InPlaceSubtract)
THUNK_INPLACE(thunk_imul, PyNumber_InPlaceMultiply)

#if NT_HAS_MATMUL
THUNK_INPLACE(thunk_imatmul, PyNumber_InPlaceMatrixMultiply)
#endif

THUNK_INPLACE(thunk_ifloordiv, PyNumber_InPlaceFloorDivide)
THUNK_INPLACE(thunk_itruediv, PyNumber_InPlaceTrueDivide)
THUNK_INPLACE(thunk_irem, PyNumber_InPlaceRemainder)
THUNK_INPLACE(thunk_ilshift, PyNumber_InPlaceLshift)
THUNK_INPLACE(thunk_irshift, PyNumber_InPlaceRshift)
THUNK_INPLACE(thunk_iand, PyNumber_InPlaceAnd)
THUNK_INPLACE(thunk_ixor, PyNumber_InPlaceXor)
THUNK_INPLACE(thunk_ior, PyNumber_InPlaceOr)

static PyObject *
thunk_ipower(PyObject *a, PyObject *b, PyObject *c)
{
    PyObject *val;

    if (PyObject_IsInstance(a, (PyObject*) &thunk_type)) {
        val = _strict_eval_borrowed(a);
        return PyNumber_InPlacePower(val, b, c);
    }
    else {
        val = _strict_eval_borrowed(b);
        return PyNumber_InPlacePower(a, val, c);
    }
}

/* Unary operators ---------------------------------------------------------- */

#define THUNK_UNOP(name, func)                                          \
    static PyObject *                                                   \
    name(PyObject *self)                                                \
    {                                                                   \
        PyObject *fn;                                                   \
        PyObject *arg;                                                  \
        PyObject *ret;                                                  \
        if (!(fn = unarywrapper_from_func(func))) {                     \
            return NULL;                                                \
        }                                                               \
        if (!(arg = PyTuple_Pack(1, self))) {                           \
            Py_DECREF(fn);                                              \
            return NULL;                                                \
        }                                                               \
        ret = _thunk_new_no_check(Py_TYPE(self), fn, arg, NULL);        \
        Py_DECREF(fn);                                                  \
        Py_DECREF(arg);                                                 \
        return ret;                                                     \
    }

THUNK_UNOP(thunk_neg, PyNumber_Negative)
THUNK_UNOP(thunk_pos, PyNumber_Positive)
THUNK_UNOP(thunk_abs, PyNumber_Absolute)
THUNK_UNOP(thunk_inv, PyNumber_Invert)

/* Ternary operators ------------------------------------------------------- */

static PyObject *
thunk_power(PyObject *a, PyObject *b, PyObject *c)
{
    PyObject *fn;
    PyObject *arg;
    PyObject *ret;
    int instance_p;

    if (!(fn = ternarywrapper_from_func(PyNumber_Power))) {
        return NULL;
    }

    if (!(arg = PyTuple_Pack(3, a, b, c))) {
        Py_DECREF(fn);
        return NULL;
    }

    if ((instance_p = PyObject_IsInstance(a, (PyObject*) &thunk_type)) == -1) {
        Py_DECREF(fn);
        Py_DECREF(arg);
        return NULL;
    }
    ret = _thunk_new_no_check(Py_TYPE(instance_p ? a : b), fn, arg, NULL);
    Py_DECREF(fn);
    Py_DECREF(arg);
    return ret;
}

/* Converters -------------------------------------------------------------- */

#define THUNK_STRICT_CONVERTER(name, type, default_, func)       \
    static type                                                 \
    name(PyObject *self)                                        \
    {                                                           \
        PyObject *val;                                          \
        if (!(val = _strict_eval_borrowed(self))) {             \
            return default_;                                    \
        }                                                       \
        return func(val);                                       \
    }

THUNK_STRICT_CONVERTER(thunk_long, PyObject*, NULL, PyNumber_Long)
THUNK_STRICT_CONVERTER(thunk_float, PyObject*, NULL, PyNumber_Float)
THUNK_STRICT_CONVERTER(thunk_index, PyObject*, NULL, PyNumber_Index)
THUNK_STRICT_CONVERTER(thunk_bool, int, -1, PyObject_IsTrue)

/* As number --------------------------------------------------------------- */

static PyNumberMethods thunk_as_number = {
    (binaryfunc) thunk_add,
    (binaryfunc) thunk_sub,
    (binaryfunc) thunk_mul,
    (binaryfunc) thunk_rem,
    (binaryfunc) thunk_divmod,
    (ternaryfunc) thunk_power,
    (unaryfunc) thunk_neg,
    (unaryfunc) thunk_pos,
    (unaryfunc) thunk_abs,
    (inquiry) thunk_bool,
    (unaryfunc) thunk_inv,
    (binaryfunc) thunk_lshift,
    (binaryfunc) thunk_rshift,
    (binaryfunc) thunk_and,
    (binaryfunc) thunk_xor,
    (binaryfunc) thunk_or,
    (unaryfunc) thunk_long,
    NULL,  /* reserved slot */
    (unaryfunc) thunk_float,
    (binaryfunc) thunk_iadd,
    (binaryfunc) thunk_isub,
    (binaryfunc) thunk_imul,
    (binaryfunc) thunk_irem,
    (ternaryfunc) thunk_ipower,
    (binaryfunc) thunk_ilshift,
    (binaryfunc) thunk_irshift,
    (binaryfunc) thunk_iand,
    (binaryfunc) thunk_ixor,
    (binaryfunc) thunk_ior,
    (binaryfunc) thunk_floordiv,
    (binaryfunc) thunk_truediv,
    (binaryfunc) thunk_ifloordiv,
    (binaryfunc) thunk_itruediv,
    (unaryfunc) thunk_index,

#if NT_HAS_MATMUL
    (binaryfunc) thunk_matmul,
    (binaryfunc) thunk_imatmul,
#endif

};

/* As mapping -------------------------------------------------------------- */

static Py_ssize_t
thunk_len(PyObject *self)
{
    PyObject *val;

    if (!(val = _strict_eval_borrowed(self))) {
        return -1;
    }

    return PyObject_Size(val);
}

static PyObject *
thunk_getitem(PyObject *self, PyObject *key)
{
    PyObject *func;
    PyObject *arg;
    PyObject *ret;

    if (!(func = binwrapper_from_func(PyObject_GetItem))) {
        return NULL;
    }

    if (!(arg = Py_BuildValue("(OO)", self, key))) {
        Py_DECREF(func);
        return NULL;
    }
    ret = _thunk_new_no_check(Py_TYPE(self), func, arg, NULL);
    Py_DECREF(func);
    Py_DECREF(arg);
    return ret;
}

static int
thunk_setitem(PyObject *self, PyObject *key, PyObject *value)
{
    PyObject *val;

    if (!(val = _strict_eval_borrowed(self))) {
        return -1;
    }

    PyObject_SetItem(val, key, value);
    return 0;
}

static PyMappingMethods thunk_as_mapping = {
    (lenfunc) thunk_len,
    (binaryfunc) thunk_getitem,
    (objobjargproc) thunk_setitem,
};

/* Misc methods ------------------------------------------------------------ */

static Py_hash_t
thunk_hash(PyObject *self)
{
    PyObject *normal;

    if (!(normal = _strict_eval_borrowed(self))) {
        return -1;
    }

    return PyObject_Hash(normal);
}

static PyObject *
thunk_call(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return _thunk_new_no_check(Py_TYPE(self), self, args, kwargs);
}

THUNK_STRICT_CONVERTER(thunk_repr, PyObject*, NULL, PyObject_Repr)
THUNK_STRICT_CONVERTER(thunk_str, PyObject*, NULL, PyObject_Str)

static PyObject *
thunk_getattro(PyObject *self, PyObject *name)
{
    PyObject *func;
    PyObject *arg;
    PyObject *ret;

    if (!PyUnicode_CompareWithASCIIString(name, "__class__")) {
        if (!(arg = _strict_eval_borrowed(self))) {
            return NULL;
        }
        return PyObject_GetAttr(arg, name);
    }

    if (!(func = binwrapper_from_func(PyObject_GetAttr))) {
        return NULL;
    }

    if (!(arg = PyTuple_Pack(2, self, name))) {
        Py_DECREF(func);
        return NULL;
    }
    ret = _thunk_new_no_check(Py_TYPE(self), func, arg, NULL);
    Py_DECREF(func);
    Py_DECREF(arg);
    return ret;
}

static int
thunk_setattro(PyObject *self, PyObject *name, PyObject *value)
{
    PyObject *normal;

    if (!(normal = _strict_eval_borrowed(self))) {
        return -1;
    }

    return PyObject_SetAttr(normal, name, value);
}

static int
thunk_traverse(thunk *self, visitproc visit, void *arg)
{
    if (self->th_func) {
        Py_VISIT(self->th_func);
    }
    if (self->th_args) {
        Py_VISIT(self->th_args);
    }
    if (self->th_kwargs) {
        Py_VISIT(self->th_kwargs);
    }
    if (self->th_normal) {
        Py_VISIT(self->th_normal);
    }
    return 0;
}

static int
thunk_clear(thunk *self)
{
    Py_CLEAR(self->th_func);
    Py_CLEAR(self->th_args);
    Py_CLEAR(self->th_kwargs);
    Py_CLEAR(self->th_normal);
    return 0;
}


THUNK_UNOP(thunk_iter, PyObject_GetIter)

static PyObject *
_id(PyObject *a)
{
    Py_INCREF(a);
    return a;
}

/* Returns the _id_callable singleton.
   return: A new reference. */
static PyObject *
_get_id(void)
{
    static PyObject *_id_callable = NULL;

    if (!_id_callable && !(_id_callable = unarywrapper_from_func(_id))) {
        return NULL;
    }

    Py_INCREF(_id_callable);
    return _id_callable;
}

static PyObject *
thunk_next(thunk *self)
{
    PyObject *fn;
    PyObject *arg;
    PyObject *tmp;
    PyObject *ret;

    if (!(fn = _get_id())) {
        return NULL;
    }

    if (!(tmp = _strict_eval_borrowed((PyObject*) self))) {
        Py_DECREF(fn);
        return NULL;
    }

    if (!PyIter_Check(tmp)) {
        PyErr_Format(PyExc_TypeError,
                     "'%s' object is not an iterator'",
                     Py_TYPE(tmp)->tp_name);
        return NULL;
    }

    if (!(tmp = PyIter_Next(tmp)) || PyErr_Occurred()) {
        return NULL;
    }

    if (!(arg = PyTuple_Pack(1, tmp))) {
        Py_DECREF(fn);
        return NULL;
    }

    ret = _thunk_new_no_check(Py_TYPE(self), fn, arg, NULL);
    Py_DECREF(fn);
    Py_DECREF(arg);
    return ret;
}

/* Rich compare helpers ---------------------------------------------------- */

#define THUNK_CMPOP(name, op)                                           \
    static PyObject *                                                   \
    name(PyObject *self, PyObject *other)                               \
    {                                                                   \
        return PyObject_RichCompare(self, other, op);                   \
    }

THUNK_CMPOP(thunk_lt, Py_LT)
THUNK_CMPOP(thunk_le, Py_LE)
THUNK_CMPOP(thunk_eq, Py_EQ)
THUNK_CMPOP(thunk_ne, Py_NE)
THUNK_CMPOP(thunk_gt, Py_GT)
THUNK_CMPOP(thunk_ge, Py_GE)

static PyObject *
thunk_richcmp(thunk *self, PyObject *other, int op)
{
    PyObject *(*f)(PyObject*,PyObject*);
    PyObject *func;
    PyObject *arg;
    PyObject *ret;

    if (!(arg = PyTuple_Pack(2, self, other))) {
        return NULL;
    }

    switch(op) {
    case Py_LT:
        f = thunk_lt;
        break;
    case Py_LE:
        f = thunk_le;
        break;
    case Py_EQ:
        f = thunk_eq;
        break;
    case Py_NE:
        f = thunk_ne;
        break;
    case Py_GT:
        f = thunk_gt;
        break;
    case Py_GE:
        f = thunk_ge;
        break;
    default:
      Py_DECREF(arg);
      PyErr_BadInternalCall();
      return NULL;
    }

    if (!(func = binwrapper_from_func(f))) {
        Py_DECREF(arg);
        return NULL;
    }
    ret = _thunk_new_no_check(Py_TYPE(self), func, arg, NULL);
    Py_DECREF(func);
    Py_DECREF(arg);
    return ret;
}

/* Extra methods ----------------------------------------------------------- */

/* Create a thunk that wraps a single value. */
static PyObject *
thunk_fromvalue(PyObject *cls, PyObject *value)
{
    PyObject *fn;
    PyObject *ret;
    PyObject *arg;

    if (PyObject_IsInstance(value, (PyObject*) &PyType_Type) &&
        PyObject_IsSubclass(value, (PyObject*) &strict_type)) {
        Py_INCREF(value);
        return value;
    }

    if (!(fn = _get_id())) {
        return NULL;
    }

    if (!(arg = PyTuple_Pack(1, value))) {
        Py_DECREF(fn);
        return NULL;
    }

    ret = _thunk_new_no_check((PyTypeObject*) cls, fn, arg, NULL);
    Py_DECREF(arg);
    Py_DECREF(fn);
    return ret;
}

PyDoc_STRVAR(thunk_fromvalue_doc, "Create a thunk that wraps a single value");

PyMethodDef thunk_methods[] = {
    {"fromvalue", thunk_fromvalue, METH_CLASS | METH_O, thunk_fromvalue_doc},
    {NULL},
};

/* thunk definition -------------------------------------------------------- */

PyDoc_STRVAR(thunk_doc, "A deferred computation.");

static PyTypeObject thunk_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "lazy._thunk.thunk",                        /* tp_name */
    sizeof(thunk),                              /* tp_basicsize */
    0,                                          /* tp_itemsize */
    (destructor) thunk_dealloc,                 /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    (reprfunc) thunk_repr,                      /* tp_repr */
    &thunk_as_number,                           /* tp_as_number */
    0,                                          /* tp_as_sequence */
    &thunk_as_mapping,                          /* tp_as_mapping */
    (hashfunc) thunk_hash,                      /* tp_hash */
    (ternaryfunc) thunk_call,                   /* tp_call */
    (reprfunc) thunk_str,                       /* tp_str */
    (getattrofunc) thunk_getattro,              /* tp_getattro */
    (setattrofunc) thunk_setattro,              /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT
    | Py_TPFLAGS_BASETYPE
    | Py_TPFLAGS_HAVE_GC,                       /* tp_flags */
    thunk_doc,                                  /* tp_doc */
    (traverseproc) thunk_traverse,              /* tp_traverse */
    (inquiry) thunk_clear,                      /* tp_clear */
    (richcmpfunc) thunk_richcmp,                /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    (getiterfunc) thunk_iter,                   /* tp_iter */
    (iternextfunc) thunk_next,                  /* tp_iternext */
    thunk_methods,                              /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    &PyBaseObject_Type,                         /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    (allocfunc) thunk_alloc,                    /* tp_alloc */
    (newfunc) thunk_new,                        /* tp_new */
    (freefunc) thunk_free,                      /* tp_free */
};

/* Module level ------------------------------------------------------------ */

PyDoc_STRVAR(module_doc,"A defered computation.");

static struct PyModuleDef _thunk_module = {
    PyModuleDef_HEAD_INIT,
    "lazy._thunk",
    module_doc,
    -1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__thunk(void)
{
    PyObject *m;
    PyTypeObject *types[] = {&unarywrapper_type,
                             &binwrapper_type,
                             &ternarywrapper_type,
                             &strict_type,
                             &thunk_type,
                             NULL};
    size_t n = 0;

    while (types[n]) {
        if (PyType_Ready(types[n])) {
            return NULL;
        }
        ++n;
    }

    if (!(m = PyModule_Create(&_thunk_module))) {
        return NULL;
    }

    if (PyObject_SetAttrString(m, "thunk", (PyObject*) &thunk_type)) {
        Py_DECREF(m);
        return NULL;
    }

    if (PyObject_SetAttrString(m, "strict", (PyObject*) &strict_type)) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
