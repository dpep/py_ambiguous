from collections import Iterable

from .decorator import decorator


@decorator
def thing_or_things(fn, offset=0):
  def wrapper(*args, **kwargs):
    if len(args) < offset:
      raise ValueError(
        '%s() takes at least %d argument (%d given)' % (
          fn.__name__, offset, len(args),
        )
      )

    prefix_args = list(args[:offset])
    things = list(args[offset:])

    unpacked = False
    if 1 == len(things) and isinstance(things[0], (list, set, tuple)):
        things = things[0]
        unpacked = True

    res = fn(*(prefix_args + [ things ]), **kwargs)
    if not unpacked and 1 == len(things):
      res = res[things[0]]

    return res
  return wrapper
