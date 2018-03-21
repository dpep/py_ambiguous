#!/usr/bin/python

import os
import sys
import unittest

from functools import wraps

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous.decorator import is_self


class DecoratorIsSelfTest(unittest.TestCase):

    def test_is_self(self):
        class Foo():
            def foo(self):
                return is_self(Foo.foo, self)

            @classmethod
            def bar(cls):
                return is_self(Foo.bar, cls)

            @staticmethod
            def baz(arg):
                return is_self(Foo.baz, arg)

        foo = Foo()

        self.assertTrue(Foo().foo())
        self.assertFalse(Foo.bar())
        self.assertFalse(Foo().bar())
        self.assertFalse(Foo.baz(foo))
        self.assertFalse(Foo.baz(foo))
        self.assertFalse(Foo().baz(foo))


    def test_sanity(self):
        def foo(arg): return is_self(foo, arg)
        self.assertFalse(foo('str'))


    def test_decorator(self):
        def check_self(fn):
            @wraps(fn)
            def wrapper(*args):
                return (
                    is_self(wrapper, *args),
                    fn(*args),
                )
            return wrapper

        class Foo():
            @check_self
            def foo(self, arg): return arg

            @classmethod
            @check_self
            def bar(cls, arg): return arg

            @staticmethod
            @check_self
            def baz(arg): return arg


        foo = Foo()

        self.assertEqual(
            (True, foo),
            Foo().foo(foo)
        )
        self.assertEqual(
            (False, foo),
            Foo.bar(foo)
        )
        self.assertEqual(
            (False, foo),
            Foo().bar(foo)
        )
        self.assertEqual(
            (False, foo),
            Foo.baz(foo)
        )
        self.assertEqual(
            (False, foo),
            Foo().baz(foo)
        )


    def test_class_decorator(self):
        class Bar():
            @staticmethod
            def check_self(fn):
                @wraps(fn)
                def wrapper(*args):
                    return is_self(wrapper, *args)
                return wrapper

        class Baz():
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



if __name__ == '__main__':
    unittest.main()
