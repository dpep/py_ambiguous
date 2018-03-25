import inspect
import types


__all__ = [
  'same_method',
]


def same_method(fn1, fn2):
  if fn1.__name__ != fn2.__name__:
    return False

  if str(fn1) != str(fn2):
    return False

  # to be extra certain, check the code itself
  code_attrs = [
    'co_filename',
    'co_firstlineno',
    'co_code',
  ]
  for attr in code_attrs:
    if getattr(fn1.__code__, attr) != getattr(fn2.__code__, attr):
      return False

  return True


def within_self(class_method, *args):
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


def within_class(class_method, *args):
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
