import sys
import types

from functools import partial
from types import *

from .ops import ops


__all__ = [
  'ambiguous',
  'ambiguous_method',
  'ambiguous_classmethod',
]


class AmbiguousType(object):
  pass


def ambiguous_function(func, *args, **kwargs):
  wrapper = partial(func, *args, **kwargs)

  class AmbiguousFunction(AmbiguousType):
      def __call__(self, *args, **kwargs):
        return wrapper(*args, **kwargs)

  # monkey patch pass-through wrappers for all operators and special
  # functions, eg. __eq__, __str__
  for op in ops:
    def exec_op(op, *args, **kwargs):
      def exec_op(self, *args, **kwargs):
        obj = self()
        attr = getattr(obj, op, None)

        if attr is None and op == '__getattribute__':
          # support for old style classes that do not implement
          # __getattribute__
          attr = getattr(obj, args[0], None)
          args = tuple(args[1:])

        if attr is None:
          raise AttributeError(
            "type object '%s' has no attribute '%s'" % (
              type(obj), op
            )
          )

        return attr(*args, **kwargs)
      return exec_op

    # create unbound method for op
    op_fn = types.MethodType(exec_op(op), None, AmbiguousFunction)

    # monkey patch
    setattr(AmbiguousFunction, op, op_fn)

  # call __new__ so as not to trigger pass-through __init__()
  return AmbiguousFunction.__new__(AmbiguousFunction)


def ambiguous_method(func):
  class AmbiguousMethod(AmbiguousType):
    def __get__(self, obj, objtype):
      if obj:
        # convert into an AmbiguousFunction with obj (aka self)
        # as the first arg
        return ambiguous_function(func, obj)

      # called with class not instance, so return unbound method
      return types.MethodType(func, None, objtype)

  return AmbiguousMethod()


def ambiguous_classmethod(func):
  class AmbiguousClassMethod(AmbiguousType):
    def __get__(self, obj, objtype):
      # convert into an AmbiguousFunction with objtype (aka class)
      # as the first arg
      return ambiguous_function(func, objtype)

  return AmbiguousClassMethod()


def ambiguous(func):
  if isinstance(func, (BuiltinFunctionType, FunctionType)):
    return ambiguous_function(func)

  raise NotImplementedError()
