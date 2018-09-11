__author__ = 'dpepper'
__version__ = '0.3.2'


__all__ = [
  'ambiguous',
  'method',
  'classmethod',
  'staticmethod',

  'decorator',
  'thing_or_things',
]


import sys

from .ambiguous import ambiguous, ambiguous_method, ambiguous_classmethod
from .decorator import decorator
from .thing_or_things import thing_or_things


# define aliases
method = ambiguous_method
classmethod = ambiguous_classmethod
staticmethod = ambiguous


class Ambiguous(object):

  def __init__(self, module):
    self.module = module
    self.exports = set(module.__all__)

    # add in special attrs
    for x in dir(module):
      if x.startswith('__'):
        self.exports.add(x)

  def __call__(self, func):
    # decorate Class
    # https://www.codementor.io/sheena/advanced-use-python-decorators-class-function-du107nxsv
    return ambiguous(func)


  def __getattr__(self, method):
    if method not in self.exports:
      raise AttributeError("'%s' object has no attribute '%s'" % (
        self.module.__name__, method
      ))

    return globals()[method]


  def __dir__(self):
    return list(self.exports)


  @property
  def __class__(self):
    return self.module.__class__


# overwrite module so that it's callable
sys.modules[__name__] = Ambiguous(sys.modules[__name__])
