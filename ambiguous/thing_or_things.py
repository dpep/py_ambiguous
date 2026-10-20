import inspect

from .decorator import decorator


__all__ = [ 'thing_or_things' ]


@decorator
def thing_or_things(fn, arg_name=None):
  spec = inspect.getfullargspec(fn)

  if arg_name:
    if spec.varargs == arg_name:
      raise NotImplementedError('can not use varargs')

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
    elif len(spec.args) - len(spec.defaults or []) == 1:
      # if all args have defaults except the first one
      arg_name = spec.args[0]
    else:
      raise ValueError(
        'please specify which arg to use, eg. @thing_or_things(<arg_name>)'
      )


  sig = inspect.signature(fn)

  def wrapper(*args, **kwargs):
    # bind like a real call, so the thing can be passed by keyword or default
    try:
      bound = sig.bind(*args, **kwargs)
    except TypeError as e:
      raise TypeError('%s(): %s' % (fn.__name__, e)) from None
    bound.apply_defaults()

    thing_or_things = bound.arguments[arg_name]
    single_thing = not isinstance(thing_or_things, (list, set, tuple))
    things = [ thing_or_things ] if single_thing else list(thing_or_things)

    # replace thing_or_things arg and make function call
    bound.arguments[arg_name] = things
    res = fn(*bound.args, **bound.kwargs)

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
