import inspect
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
    def exec_op(op):
      def exec_op(self, *args, **kwargs):
        # call ambiguated function to retrieve result upon which user
        # is intending to operate on
        obj = self()

        # retrieve function pointer for user-intended call
        attr = getattr(obj, op, None)

        if attr is None:
            # backwards compatibility for objects not inheritting from 'object'

            if op == '__getattribute__':
              attr = getattr(obj, args[0], None)
              args = tuple(args[1:])
            elif op == '__repr__':
              # alias __repr__ => __str__
              attr = getattr(obj, '__str__', None)

        if attr is None:
          raise AttributeError(
            "type object '%s' has no attribute '%s'" % (
              type(obj), op
            )
          )

        # make user-intended function call
        return attr(*args, **kwargs)
      return exec_op

    setattr(AmbiguousFunction, op, exec_op(op))

  # call __new__ so as not to trigger pass-through __init__()
  return AmbiguousFunction.__new__(AmbiguousFunction)


def ambiguous_method(func):
  class AmbiguousMethod(AmbiguousType):
    def __get__(self, obj, objtype):
      if obj:
        # convert into an AmbiguousFunction with obj (aka self)
        # as the first arg
        return ambiguous_function(func, obj)

      if sys.version_info[0] == 2:
        # called with class not instance, so return unbound method
        return types.MethodType(func, None, objtype)
      else:
        # unbounded functions are just functions in Python3
        return func

  return AmbiguousMethod()


def ambiguous_classmethod(func):
  class AmbiguousClassMethod(AmbiguousType):
    def __get__(self, obj, objtype):
      # convert into an AmbiguousFunction with objtype (aka class)
      # as the first arg
      return ambiguous_function(func, objtype)

  return AmbiguousClassMethod()


def ambiguous_descriptor(desc):
  class AmbiguousDescriptor(AmbiguousType):
    def __get__(self, obj, objtype):
      return ambiguous_function(desc.__get__(obj, objtype))

  return AmbiguousDescriptor()


def ambiguous_class(cls):
  class_dict = getattr(cls, '__dict__')

  for name, func in inspect.getmembers(cls):
    # skip anything that isn't a method or function, eg. class var
    if not isinstance(func, (MethodType, FunctionType)):
      continue

    # skip all special methods because we're liable to get into trouble
    if name.startswith('__'):
      continue

    # use function pointer from __dict__ to determine type
    # because it contains classmethod / staticmethod info
    func_type = type(class_dict.get(name, None))

    # determine how to wrap the function
    if classmethod == func_type:
      # already a bound class method, no need to rebind
      wrapper = ambiguous_function(func)
    elif staticmethod == func_type:
      wrapper = ambiguous_function(func)
    elif FunctionType == func_type:
      # instance method
      wrapper = ambiguous_method(func)
    else:
      # inherited method...not yet implemented
      continue

    # wrap original method so it can be used ambiguously
    setattr(cls, name, wrapper)

  return cls


def ambiguous(obj):
  if isinstance(obj, (BuiltinFunctionType, FunctionType)):
    return ambiguous_function(obj)

  if isinstance(obj, type):
    return ambiguous_class(obj)

  if isinstance(obj, (classmethod, staticmethod)):
    return ambiguous_descriptor(obj)

  raise NotImplementedError('unsupported type: %s' % type(obj))
