import types

from functools import partial, wraps, update_wrapper
from inspect import isfunction

from .inspector import same_method


__all__ = [ 'decorator' ]


"""
Enable a decorator to accept args and kwargs.  Positional args
may not be callable when used via `@decorator`.
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


def is_self(class_method, *args):
  if 0 == len(args):
    return False

  self = args[0]

  if type(self) != types.InstanceType:
    return False

  if type(class_method) == types.MethodType:
    if class_method.im_self:
      # class method
      return False

    if class_method.im_class != self.__class__:
      # instance method, but for different class
      return False

    # convert class method into function
    # eg. <unbound method Foo.bar> => <function bar>
    function = class_method.im_func
  elif type(class_method) == types.FunctionType:
    # used via decorators on class methods
    function = class_method
  else:
    raise ValueError('expected class method, found: %s' % class_method)

  # does class method exist
  bound_fn = getattr(self, function.__name__, None)

  if not bound_fn or type(bound_fn) != types.MethodType:
    return False

  # compare wrapper with unbound class method
  unbound_fn = getattr(bound_fn, 'im_func', bound_fn)
  return same_method(function, unbound_fn)


def is_class(class_method, *args):
  if 0 == len(args):
    return False

  cls = args[0]

  if type(cls) != types.ClassType:
    return False

  if type(class_method) == types.MethodType:
    if not class_method.im_self:
      # instance method
      return False

    if class_method.im_self != cls:
      # class method, but for different class
      return False

    # convert class method into function
    # eg. <unbound method Foo.bar> => <function bar>
    function = class_method.im_func
  elif type(class_method) == types.FunctionType:
    # used via decorators on class methods
    function = class_method
  else:
    raise ValueError('expected class method, found: %s' % class_method)

  # does class method exist
  unbound_fn = getattr(cls, function.__name__, None)

  if not unbound_fn or type(unbound_fn) != types.MethodType:
    return False

  return same_method(
    function,
    getattr(cls, function.__name__).im_func
  )
