import inspect

from collections import Iterable
from functools import wraps

from .decorator import decorator


__all__ = [ 'thing_or_things' ]


@decorator
def thing_or_things(fn, arg_name=None):
  spec = inspect.getargspec(fn)

  if arg_name:
    if spec.varargs == arg_name:
      raise NotImplementedError('a varargs should not be used')

    if arg_name not in spec.args:
      raise ValueError(
        'arg_name not in function signature: %s' % arg_name
      )
  else:
    # no args given, determine defaults

    if spec.varargs:
      raise NotImplementedError(
        'please specify which arg to use, eg. @thing_or_things(<arg_name>)'
      )

    if not spec.args:
      raise TypeError('function does not take arguments')

    if len(spec.args) == 1:
      # grab first and only arg
      arg_name = spec.args[0]
    elif len(spec.args) - len(spec.defaults) == 1:
      # if all args have defaults except the first one
      arg_name = spec.args[0]
    else:
      raise ValueError(
        'please specify which arg to use, eg. @thing_or_things(<arg_name>)'
      )


  def wrapper(*args, **kwargs):
    single_thing = False

    # grab specified thing_or_things arg
    offset = spec.args.index(arg_name)

    if len(args) < len(spec.args) - len(spec.defaults or []):
      # not enough args...let function raise TypeError
      fn(*args, **kwargs)
      assert False, '%s() is missing arguments' % fn.__name__

    if isinstance(args[offset], (list, set, tuple)):
      # cast to list
      things = list(args[offset])
    else:
      # pack into list
      things = [ args[offset] ]
      single_thing = True

    # replace thing_or_things arg and make function call
    args = list(args)
    args[offset] = things
    res = fn(*args, **kwargs)

    if res is None:
      return

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
    if single_thing:
      res = res[things[0]]

    return res
  return wrapper
