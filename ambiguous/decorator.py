import types

from functools import partial, wraps, update_wrapper
from inspect import isfunction


__all__ = [ 'decorator' ]


"""
Enable a decorator to accept args and kwargs.
"""
def decorator(decorator_fn):
  @wraps(decorator_fn)
  def wrapper(*args, **kwargs):
    # called with no args...try again
    if not args and not kwargs:
      return wrapper

    if args:
      if callable(args[0]):
        # apply desired decorator
        decorated = decorator_fn(*args, **kwargs)

        if isfunction(decorated):
          # mask signature
          decorated = update_wrapper(decorated, args[0])

        return decorated

      # passed an arg, but not the function to decorate. wrap
      # and wait for more.
      @wraps(decorator_fn)
      def arg_wrapper(*more_args, **more_kwargs):
        if more_args and callable(more_args[0]):
          if len(more_args) > 1:
            # arg order is ambiguous
            raise ValueError(
              'expecting either callable or args, not both: %s' % str(more_args)
            )

          # prepend callable
          new_args = more_args + args
        else:
          # append additional args
          new_args = args + more_args

        # merge in new kwargs
        new_kwargs = dict(kwargs, **more_kwargs)

        return wrapper(*new_args, **new_kwargs)

      return arg_wrapper

    # given kwargs and still need function
    @wraps(decorator_fn)
    def kwarg_wrapper(*args, **more_kwargs):
      return wrapper(*args, **dict(kwargs, **more_kwargs))
    return kwarg_wrapper


  return wrapper
