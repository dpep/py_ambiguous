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
