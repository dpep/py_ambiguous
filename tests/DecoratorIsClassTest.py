#!/usr/bin/python

import os
import sys
import unittest

from functools import wraps

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous.decorator import is_class


class DecoratorIsClassTest(unittest.TestCase):

    def test_is_class(self):
        class Foo():
            def foo(self):
                return is_class(Foo.foo, self)

            @classmethod
            def bar(cls):
                return is_class(Foo.bar, cls)

            @staticmethod
            def baz(arg):
                return is_class(Foo.baz, arg)

        foo = Foo()

        self.assertFalse(Foo().foo())
        self.assertTrue(Foo.bar())
        self.assertTrue(Foo().bar())
        self.assertFalse(Foo.baz(foo))
        self.assertFalse(Foo().baz(foo))


    def test_sanity(self):
        def foo(arg): return is_class(foo, arg)
        self.assertFalse(foo('str'))


    def test_decorator(self):
        def check_self(fn):
            @wraps(fn)
            def wrapper(*args):
                return is_class(wrapper, *args)
            return wrapper

        class Foo():
            @check_self
            def foo(self): pass

            @classmethod
            @check_self
            def bar(cls): pass

            @staticmethod
            @check_self
            def baz(arg): pass


        foo = Foo()

        self.assertFalse(Foo().foo())
        self.assertTrue(Foo.bar())
        self.assertTrue(Foo().bar())
        self.assertFalse(Foo.baz(Foo))
        self.assertFalse(Foo.baz(foo))
        self.assertFalse(Foo().baz(foo))


    def test_trickery(self):
        def check_self(fn):
            @wraps(fn)
            def wrapper(*args):
                return is_class(wrapper, *args)
            return wrapper

        class Foo():
            @classmethod
            @check_self
            def foo(cls): pass

            @staticmethod
            @check_self
            def bar(arg): pass

        # masquerade
        class Fake():
            @classmethod
            def bar(): pass

        self.assertTrue(Foo().foo())
        self.assertFalse(Foo().bar(Foo))
        self.assertFalse(Foo().bar(Fake))



if __name__ == '__main__':
    unittest.main()
