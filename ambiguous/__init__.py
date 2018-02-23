__author__ = 'dpepper'
__version__ = '0.0.1'


__all__ = [
  'ambiguous_method',
  'ambiguous_instancemethod',
  'ambiguous_classmethod',
  'ambiguous_staticmethod',
]


from functools import partial
from ops import ops
import inspect
import types


def ambiguous_method(func, *args):
  wrapper = partial(func, *args)

  class AmbiguousMethod(object):
      def __call__(self, *args):
        return wrapper(*args)

  for op in ops:
    def exec_op(op, *args):
      return getattr(wrapper(), op)(*args)

    setattr(AmbiguousMethod, op, partial(exec_op, op))

  return AmbiguousMethod()


method = ambiguous_method
func = ambiguous_method


# instance method
def ambiguous_instancemethod(func):
  class AmbiguousInstanceMethod(object):
    def __get__(self, obj, objtype):
      if obj:
        return ambiguous_method(func, obj)

      # return unbound method
      return types.MethodType(func, None, objtype)

  return AmbiguousInstanceMethod()

instancemethod = ambiguous_instancemethod


# class method
def ambiguous_classmethod(func):
  class AmbiguousClassMethod(object):
    def __get__(self, obj, objtype):
      return ambiguous_method(func, objtype)

  return AmbiguousClassMethod()

classmethod = ambiguous_classmethod


# static method
ambiguous_staticmethod = ambiguous_method
staticmethod = ambiguous_staticmethod
