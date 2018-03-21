__author__ = 'dpepper'
__version__ = '0.2.0'


__all__ = [
  'ambiguous_method',
  'ambiguous_instancemethod',
  'ambiguous_classmethod',
  'ambiguous_staticmethod',
  'decorator',
  'thing_or_things',
]


import sys

from .ambiguous import *
from .decorator import decorator
from .thing_or_things import thing_or_things
from .inspector import same_method



# define some aliases
method = ambiguous_method
func = ambiguous_method
instancemethod = ambiguous_instancemethod
classmethod = ambiguous_classmethod
staticmethod = ambiguous_staticmethod


class Ambiguous(object):

  def __init__(self, module):
    self.module = module
    self.exports = set(module.__all__)

    # add in special attrs
    for x in dir(module):
      if x.startswith('__'):
        self.exports.add(x)

    # find and export all ambiguous method aliases
    ambiguous_methods = [
      getattr(ambiguous, x, None) for x in ambiguous.__all__
    ]
    for k, v in globals().items():
      if v in ambiguous_methods:
        self.exports.add(k)


  def __call__(self, *args):
    return ambiguous_method(*args)


  def __getattr__(self, method):
    if method not in self.exports:
      raise AttributeError("'%s' object has no attribute '%s'" % (
        self.module.__name__, method
      ))

    return globals()[method]


  def __dir__(self):
    return list(self.exports)


# overwrite module so that it's callable
sys.modules[__name__] = Ambiguous(sys.modules[__name__])
