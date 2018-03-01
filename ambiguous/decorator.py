from functools import partial


"""
Allow a decorator to accept kwargs
"""
def decorator(decorator_fn):
  def wrapper(fn=None, **kwargs):
    assert fn or len(kwargs) > 0

    if fn:
      return decorator_fn(fn, **kwargs)

    # given kwargs and still need function
    return partial(wrapper, **kwargs)

  return wrapper
