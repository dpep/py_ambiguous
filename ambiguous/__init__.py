__author__ = 'dpepper'
__version__ = '0.5.1'


__all__ = [
  'ambiguous',
  'decorator',
  'thing_or_things',
]


import sys
from types import ModuleType

from .ambiguous import ambiguous
from .decorator import decorator
from .thing_or_things import thing_or_things


def __dir__():
  # keep internals (sys, submodules, ...) out of dir() and tab completion
  return __all__ + [ x for x in globals() if x.startswith('__') ]


class _CallableModule(ModuleType):
  # enables `import ambiguous` + `@ambiguous`
  def __call__(self, target):
    return ambiguous(target)


sys.modules[__name__].__class__ = _CallableModule
