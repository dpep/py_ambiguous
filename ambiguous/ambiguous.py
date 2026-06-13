import inspect

from functools import partial
from types import BuiltinFunctionType, FunctionType, MethodType

from .ops import ops


__all__ = [
  'ambiguous',
  'ambiguous_method',
  'ambiguous_classmethod',
]


class AmbiguousType:
  pass


class AmbiguousFunction(AmbiguousType):
  def __call__(self, *args, **kwargs):
    # the wrapped partial is read out-of-band because __getattribute__ is
    # itself delegated (below), so plain `self._wrapper` would recurse
    return object.__getattribute__(self, '_wrapper')(*args, **kwargs)


def _delegate(op):
  def exec_op(self, *args, **kwargs):
    # retrieve object upon which user is intending to operate, then make
    # the user-intended function call
    return getattr(self(), op)(*args, **kwargs)
  return exec_op


# delegate all operators and special functions, eg. __eq__, __str__
for op in ops:
  setattr(AmbiguousFunction, op, _delegate(op))


def ambiguous_function(func, *args, **kwargs):
  # call __new__ so as not to trigger the delegated __init__()
  obj = AmbiguousFunction.__new__(AmbiguousFunction)

  # set directly, since __setattr__ is delegated too
  object.__setattr__(obj, '_wrapper', partial(func, *args, **kwargs))
  return obj


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
