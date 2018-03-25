from collections import Iterable
from functools import wraps

from .decorator import decorator


__all__ = [ 'thing_or_things' ]


@decorator
def thing_or_things(fn, offset=0):
  @wraps(fn)
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

    # check return type
    if not isinstance(res, dict):
      raise TypeError('expected %s, found %s' % (dict, type(res)))

    thing_set = set(things)
    key_set = set(res.keys())

    # ensure all things are mapped
    missing = thing_set - key_set
    if missing:
      raise KeyError('missing things: %s' % list(missing))

    # ensure there's no extra things
    extra = key_set - thing_set
    if extra:
      raise KeyError('extra things: %s' % list(extra))

    # unpack as needed
    if not unpacked and 1 == len(things):
      res = res[things[0]]

    return res
  return wrapper
