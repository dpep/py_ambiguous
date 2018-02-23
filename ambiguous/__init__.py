__author__ = 'dpepper'
__version__ = '0.1.0'


__all__ = [
  'ambiguous_method',
  'ambiguous_instancemethod',
  'ambiguous_classmethod',
  'ambiguous_staticmethod',
]


import sys

from ambiguous import *


# define some aliases
method = ambiguous_method
func = ambiguous_method
instancemethod = ambiguous_instancemethod
classmethod = ambiguous_classmethod
staticmethod = ambiguous_staticmethod


class Ambiguous(object):

  def __init__(self, module):
    self.module = module


  def __call__(self, *args):
    return ambiguous_method(*args)


  def __getattr__(self, method, *args):
    return getattr(self.module, method)


  def __dir__(self):
    # mascarade as the underlying module
    attrs = [ x for x in dir(self.module) if x.startswith('__') ]

    # ambiguous methods and aliases
    methods = [ getattr(ambiguous, x) for x in ambiguous.__all__ ]
    attrs.extend([ k for k, v in globals().items() if v in methods ])

    return attrs


# overwrite module so that it's callable
sys.modules[__name__] = Ambiguous(sys.modules[__name__])
