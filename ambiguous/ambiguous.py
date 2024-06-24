import inspect

from functools import partial
from types import *

from .ops import ops


__all__ = [
  'ambiguous',
  'ambiguous_method',
  'ambiguous_classmethod',
]


class AmbiguousType:
  pass


def ambiguous_function(func, *args, **kwargs):
  wrapper = partial(func, *args, **kwargs)

  class AmbiguousFunction(AmbiguousType):
    def __call__(self, *args, **kwargs):
      return wrapper(*args, **kwargs)

  # delegate all operators and special functions, eg. __eq__, __str__
  for op in ops:
    def exec_op(op):
      def exec_op(self, *args, **kwargs):
        # retrieve object upon which user is intending to operate
        obj = self()

        # retrieve function pointer for user-intended call
        attr = getattr(obj, op)

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
