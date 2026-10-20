__author__ = 'dpepper'
__version__ = '0.5.1'


__all__ = [
  'ambiguous',
  'method',
  'classmethod',
  'staticmethod',

  'decorator',
  'thing_or_things',
]


import sys
from types import ModuleType

from .ambiguous import ambiguous, ambiguous_method, ambiguous_classmethod
from .decorator import decorator
from .thing_or_things import thing_or_things


# define aliases
method = ambiguous_method
classmethod = ambiguous_classmethod
staticmethod = ambiguous


class _CallableModule(ModuleType):
  # enables `import ambiguous` + `@ambiguous`
  def __call__(self, target):
    return ambiguous(target)


sys.modules[__name__].__class__ = _CallableModule
