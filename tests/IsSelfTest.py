#!/usr/bin/python

import os
import sys
import unittest

from functools import wraps

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous.inspector import within_self



def check_self(fn):
    @wraps(fn)
    def wrapper(*args):
        return within_self(wrapper, *args)
    return wrapper


class DecoratorIsSelfTest(unittest.TestCase):


    def test_in_self(self):
        class Foo:
            def foo(self):
                return within_self(Foo.foo, self)

            @classmethod
            def bar(cls):
                return within_self(Foo.bar, cls)

            @staticmethod
            def baz(arg):
                return within_self(Foo.baz, arg)

        self.assertTrue(Foo().foo())
        self.assertFalse(Foo.bar())
        self.assertFalse(Foo().bar())

        foo = Foo()
        self.assertFalse(Foo.baz(foo))
        self.assertFalse(Foo().baz(foo))


    def test_sanity(self):
        def foo(arg): pass

        self.assertFalse(within_self(foo, foo))
        self.assertFalse(within_self(foo, 'str'))


    def test_decorator(self):
        class Foo:
            @check_self
            def foo(self): pass

            @classmethod
            @check_self
            def bar(cls): pass

            @staticmethod
            @check_self
            def baz(arg): pass


        foo = Foo()

        self.assertTrue(Foo().foo(foo))
        self.assertFalse(Foo.bar(foo))
        self.assertFalse(Foo().bar(foo))
        self.assertFalse(Foo.baz(foo))
        self.assertFalse(Foo().baz(foo))


    def test_class_decorator(self):
        class Bar:
            @staticmethod
            def check_self(fn):
                @wraps(fn)
                def wrapper(*args):
                    return within_self(wrapper, *args)
                return wrapper

        class Baz:
            @Bar.check_self
            def foo(self): pass

            @classmethod
            @Bar.check_self
            def bar(self): pass

            @staticmethod
            @Bar.check_self
            def baz(): pass

        self.assertTrue(Baz().foo())
        self.assertFalse(Baz.bar())
        self.assertFalse(Baz().bar())
        self.assertFalse(Baz.baz())
        self.assertFalse(Baz().baz())


    def test_duck_typing(self):
        class Foo:
            @check_self
            def foo(self): pass

            @staticmethod
            @check_self
            def bar(arg): pass

        class Bar:
            def bar(self): pass

        self.assertTrue(Foo().foo())
        self.assertFalse(Foo().bar(Bar))
        self.assertFalse(Foo().bar(Bar()))



if __name__ == '__main__':
    unittest.main()
