from functools import partial


"""
Enable a decorator to accept args and kwargs.  Positional args
may not be callable when used via `@decorator`.
"""
def decorator(decorator_fn):
  def wrapper(*args, **kwargs):
    assert args or kwargs

    if args:
      if callable(args[0]):
        # apply desired decorator
        return decorator_fn(*args, **kwargs)

      # passed an arg, but not the function to decorate. wrap
      # and wait for more.
      def arg_wrapper(*more_args, **more_kwargs):
        return wrapper(
          *(more_args + args),  # prepend new args
          **dict(kwargs, **more_kwargs)
        )

      return arg_wrapper

    # given kwargs and still need function
    return partial(wrapper, **kwargs)

  return wrapper
