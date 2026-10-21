import operator
from functools import partial
from types import BuiltinFunctionType, FunctionType

from .ops import ops

__all__ = ["ambiguous"]


class AmbiguousFunction:
    def __call__(self, *args, **kwargs):
        # the wrapped partial is read out-of-band because __getattribute__ is
        # itself delegated (below), so plain `self._wrapper` would recurse
        return object.__getattribute__(self, "_wrapper")(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        # bind like a plain function, so @ambiguous works on methods
        wrapper = object.__getattribute__(self, "_wrapper")
        if obj is None:
            return wrapper.func

        return ambiguous_function(wrapper.func, obj, *wrapper.args, **wrapper.keywords)


def _delegate(op):
    # operators go through the operator module rather than the result's own
    # dunder, so Python's fallbacks still apply: __bool__ -> __len__,
    # NotImplemented -> reflected op, mixed types (1 == 1.0, "a" + proxy)
    if op == "__bool__":
        return lambda self: bool(self())

    # 3-arg pow() has no operator equivalent
    if op in _operators and op != "__pow__":
        fn = _operators[op]
        return lambda self, *args: fn(self(), *args)

    # reflected, eg. __radd__ -> operator.__add__(other, result)
    forward = "__" + op.removeprefix("__r")
    if op.startswith("__r") and forward in _operators:
        fn = _operators[forward]
        return lambda self, other: fn(other, self())

    def exec_op(self, *args, **kwargs):
        # retrieve object upon which user is intending to operate, then make
        # the user-intended function call
        return getattr(self(), op)(*args, **kwargs)

    return exec_op


# vars(), not getattr(): the module's own __eq__, __hash__, etc. aren't operators
_operators = vars(operator)


# delegate all operators and special functions, eg. __eq__, __str__
for op in ops:
    setattr(AmbiguousFunction, op, _delegate(op))


def ambiguous_function(func, *args, **kwargs):
    # call __new__ so as not to trigger the delegated __init__()
    obj = AmbiguousFunction.__new__(AmbiguousFunction)

    # set directly, since __setattr__ is delegated too
    object.__setattr__(obj, "_wrapper", partial(func, *args, **kwargs))
    return obj


class _AmbiguousDescriptor:
    # wraps a classmethod / staticmethod, binding at lookup so that
    # subclasses get their own cls
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, obj, objtype=None):
        return ambiguous_function(self.desc.__get__(obj, objtype))


def ambiguous_class(cls):
    # only the class's own attrs, so inherited methods are left alone
    for name, attr in list(vars(cls).items()):
        # skip special methods because we're liable to get into trouble
        if name.startswith("__"):
            continue

        if isinstance(attr, (FunctionType, classmethod, staticmethod)):
            setattr(cls, name, ambiguous(attr))

    return cls


def ambiguous(obj):
    if isinstance(obj, (BuiltinFunctionType, FunctionType)):
        return ambiguous_function(obj)

    if isinstance(obj, type):
        return ambiguous_class(obj)

    if isinstance(obj, (classmethod, staticmethod)):
        return _AmbiguousDescriptor(obj)

    raise TypeError(
        f"expected a function, class, classmethod or staticmethod, got {type(obj).__name__}"
    )
