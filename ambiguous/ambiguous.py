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

    def __set_name__(self, owner, name):
        # called for each value in a class body. Swap in a plain method
        # descriptor: abc, dataclasses and pydoc read the class namespace, and
        # a proxy there would answer them by calling the method without self
        wrapper = object.__getattribute__(self, "_wrapper")

        # builtins and already-bound methods don't bind self, as in plain Python
        if isinstance(wrapper.func, FunctionType) and not wrapper.args:
            setattr(owner, name, _AmbiguousMethod(wrapper.func))


# vars(), not getattr(): the module's own __eq__, __hash__, etc. aren't operators
_operators = vars(operator)


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

    return lambda self, *args, **kwargs: getattr(self(), op)(*args, **kwargs)


# delegate all operators and special functions, eg. __eq__, __str__
for op in ops:
    setattr(AmbiguousFunction, op, _delegate(op))


def _ambiguous_function(func, *args):
    # call __new__ so as not to trigger the delegated __init__()
    obj = AmbiguousFunction.__new__(AmbiguousFunction)

    # set directly, since __setattr__ is delegated too
    object.__setattr__(obj, "_wrapper", partial(func, *args))
    return obj


class _AmbiguousMethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func

        # bind obj (aka self) as the first arg
        return _ambiguous_function(self.func, obj)


class _AmbiguousDescriptor:
    # wraps a classmethod / staticmethod, binding at lookup so that
    # subclasses get their own cls
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, obj, objtype=None):
        return _ambiguous_function(self.desc.__get__(obj, objtype))


def _ambiguous_class(cls):
    # only the class's own attrs, so inherited methods are left alone
    for name, attr in list(vars(cls).items()):
        # the interpreter calls dunders itself, so optional parentheses buy
        # nothing there
        if name.startswith("__"):
            continue

        if isinstance(attr, FunctionType):
            setattr(cls, name, _AmbiguousMethod(attr))
        elif isinstance(attr, (classmethod, staticmethod)):
            setattr(cls, name, _AmbiguousDescriptor(attr))

    return cls


def ambiguous(obj):
    """
    Make parentheses optional: `foo` acts like `foo()`, and `foo(x)` still works.

    Takes a function, a classmethod / staticmethod, or a class (whose own
    methods, except dunders, all become ambiguous). The result is computed
    afresh on each use and is never cached.
    """
    if isinstance(obj, (BuiltinFunctionType, FunctionType)):
        return _ambiguous_function(obj)

    if isinstance(obj, type):
        return _ambiguous_class(obj)

    if isinstance(obj, (classmethod, staticmethod)):
        return _AmbiguousDescriptor(obj)

    raise TypeError(
        f"expected a function, class, classmethod or staticmethod, got {type(obj).__name__}"
    )
