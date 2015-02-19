import ast

from lazy.utils import isolate_namespace


class DispatchMeta(type):
    """
    Allows methods to dispatch to ast visit_* methods
    when they have been decorated with register_types.
    """
    def __new__(mcls, name, bases, dict_):
        for v in dict(dict_).values():
            types = getattr(v, '_types', ())
            for type_ in types:
                dict_['visit_' + type_.__name__] = v

        return type.__new__(mcls, name,  bases, dict_)


def register_types(*types):
    """
    Add types to be dispatched on by a method.
    """
    def decorator(f):
        f._types = types
        return f

    return decorator


class LazyTransformer(ast.NodeTransformer, metaclass=DispatchMeta):
    """
    Parses a python syntax tree and creates a lazy one.
    """
    THUNK = isolate_namespace('thunk')

    @register_types(
        ast.Num,
        ast.Str,
    )
    def _wrap_lambda_thunk(self, body):
        return ast.fix_missing_locations(
            ast.Call(
                func=ast.Name(
                    id=self.THUNK,
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Lambda(
                        args=ast.arguments(
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[],
                        ),
                        body=body,
                    ),
                ],
                keywords=[],
                starargs=None,
                kwargs=None,
                lineno=body.lineno,
                col_offset=body.col_offset,
            ),
        )

    @register_types(
        ast.Dict,
        ast.Set,
        ast.List,
        ast.Tuple,
    )
    def _recursive_thunk(self, node):
        node = self.generic_visit(node)
        return self._wrap_lambda_thunk(node)

    def visit_Call(self, node):
        node = self.generic_visit(node)
        return ast.fix_missing_locations(
            ast.Call(
                func=ast.Name(
                    id=self.THUNK,
                    ctx=ast.Load(),
                ),
                args=[
                    node.func,
                ] + node.args,
                keywords=node.keywords,
                starargs=node.starargs,
                kwargs=node.kwargs,
                lineno=node.lineno,
                col_offset=node.col_offset,
            ),
        )

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            return self._wrap_lambda_thunk(node)
        else:
            return node
