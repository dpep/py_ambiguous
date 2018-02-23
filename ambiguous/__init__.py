__author__ = 'dpepper'
__version__ = '0.0.1'


__all__ = [
  'ambiguous_function',
  'ambiguous_instancemethod',
  'ambiguous_classmethod',
  'ambiguous_staticmethod',
]


from functools import partial
from ops import ops
import inspect
import types


def ambiguous_function(func, *args):
  wrapper = partial(func, *args)

  class AmbiguousFunction(object):
      def __call__(self, *args):
        return wrapper(*args)

  for op in ops:
    def exec_op(op, *args):
      return getattr(wrapper(), op)(*args)

    setattr(AmbiguousFunction, op, partial(exec_op, op))

  return AmbiguousFunction()


function = ambiguous_function
func = ambiguous_function


# instance method
def ambiguous_instancemethod(func):
  class AmbiguousInstanceMethod(object):
    def __get__(self, obj, objtype):
      if obj:
        return ambiguous_function(func, obj)

      # return unbound method
      return types.MethodType(func, None, objtype)

  return AmbiguousInstanceMethod()

instancemethod = ambiguous_instancemethod


# class method
def ambiguous_classmethod(func):
  class AmbiguousClassMethod(object):
    def __get__(self, obj, objtype):
      return ambiguous_function(func, objtype)

  return AmbiguousClassMethod()

classmethod = ambiguous_classmethod


# static method
ambiguous_staticmethod = ambiguous_function
staticmethod = ambiguous_staticmethod
