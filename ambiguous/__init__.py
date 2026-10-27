"""
flexibility when you need it

- ambiguous: make parentheses optional on a function, method or class's methods
- decorator: let a decorator be used with or without arguments
- thing_or_things: let a function take one thing or a collection of them
"""

__author__ = "dpepper"
__version__ = "0.5.2"


__all__ = [
    "ambiguous",
    "decorator",
    "thing_or_things",
]


import sys
from types import ModuleType

from .ambiguous import ambiguous
from .decorator import decorator
from .thing_or_things import thing_or_things


def __dir__():
    # keep internals (sys, submodules, ...) out of dir() and tab completion
    return __all__ + [x for x in globals() if x.startswith("__")]


class _CallableModule(ModuleType):
    # enables `import ambiguous` + `@ambiguous`
    def __call__(self, target):
        return ambiguous(target)


sys.modules[__name__].__class__ = _CallableModule
