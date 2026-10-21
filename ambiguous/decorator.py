from functools import update_wrapper, wraps
from inspect import isfunction

__all__ = [ 'decorator' ]


def decorator(decorator_fn):
  """
  Enable a decorator to accept args and kwargs.
  """
  @wraps(decorator_fn)
  def wrapper(*args, **kwargs):
    if args and callable(args[0]):
      # apply desired decorator
      decorated = decorator_fn(*args, **kwargs)

      # mask signature, unless the target was returned as-is, which
      # would make it its own __wrapped__
      if isfunction(decorated) and decorated is not args[0]:
        update_wrapper(decorated, args[0])

      return decorated

    # no function to decorate yet. wrap and accumulate args and kwargs
    # until it arrives.
    @wraps(decorator_fn)
    def collect(*more_args, **more_kwargs):
      if more_args and callable(more_args[0]):
        if args and len(more_args) > 1:
          # arg order is ambiguous
          raise ValueError(
            f'expecting either callable or args, not both: {more_args}'
          )

        # prepend callable
        new_args = more_args + args
      else:
        # append additional args
        new_args = args + more_args

      return wrapper(*new_args, **{ **kwargs, **more_kwargs })

    return collect

  return wrapper
