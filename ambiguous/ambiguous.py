import inspect
import math
import operator
import os
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
        func = wrapper.func

        # only methods defined in this class body bind self. A function
        # assigned from elsewhere stays a value, eg. `region = default_region`,
        # as do builtins and already-bound methods
        defined_here = getattr(func, "__qualname__", "").startswith(
            owner.__qualname__ + "."
        )
        if isinstance(func, FunctionType) and defined_here and not wrapper.args:
            setattr(owner, name, _AmbiguousMethod(func))


# vars(), not getattr(): the module's own __eq__, __hash__, etc. aren't operators
_operators = vars(operator)

# protocols whose builtin adds fallbacks the bare dunder lacks, eg. int(str),
# reversed(sequence), math.floor(float), mixed-type pow / divmod, 3-arg pow
_builtins = {
    "__ceil__": math.ceil,
    "__complex__": complex,
    "__divmod__": divmod,
    "__float__": float,
    "__floor__": math.floor,
    "__fspath__": os.fspath,
    "__hash__": hash,
    "__int__": int,
    "__iter__": iter,
    "__len__": len,
    "__pow__": pow,
    "__reversed__": reversed,
    "__round__": round,
    "__trunc__": math.trunc,
}
_reflected_builtins = {"__rdivmod__": divmod, "__rpow__": pow}


def _delegate(op):
    # operators go through the operator module rather than the result's own
    # dunder, so Python's fallbacks still apply: __bool__ -> __len__,
    # NotImplemented -> reflected op, mixed types (1 == 1.0, "a" + proxy)
    if op == "__bool__":
        return lambda self: bool(self())

    if op in _builtins:
        fn = _builtins[op]
        return lambda self, *args: fn(self(), *args)

    # 3-arg pow(base, proxy, mod) passes mod to __rpow__ on 3.14+
    if op in _reflected_builtins:
        fn = _reflected_builtins[op]
        return lambda self, other, *args: fn(other, self(), *args)

    if op in _operators:
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

    # abc reads this off each class attr to find abstract methods
    @property
    def __isabstractmethod__(self):
        return getattr(self.func, "__isabstractmethod__", False)

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

    @property
    def __isabstractmethod__(self):
        return self.desc.__isabstractmethod__

    def __get__(self, obj, objtype=None):
        return _ambiguous_function(self.desc.__get__(obj, objtype))


def _ambiguous_class(cls):
    # only the class's own attrs, so inherited methods are left alone
    for name, attr in list(vars(cls).items()):
        # the interpreter calls dunders itself, so optional parentheses buy
        # nothing there
        if name.startswith("__"):
            continue

        # `await` needs the coroutine itself, and async frameworks detect
        # coroutine functions by inspecting the method
        func = getattr(attr, "__func__", attr)
        if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
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
    methods, except dunders and async ones, all become ambiguous). The result is computed
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
