__author__ = 'dpepper'
__version__ = '0.0.1'


__all__ = [
  'function',
]


from functools import partial
from ops import ops


def ambiguous_function(func):
  class AmbiguousFunction(object):
      def __call__(self, *args):
        return func(*args)

  for op in ops:
    def exec_op(op, *args):
      return getattr(func(), op)(*args)

    setattr(AmbiguousFunction, op, partial(exec_op, op))

  return AmbiguousFunction()


function = ambiguous_function
func = ambiguous_function
