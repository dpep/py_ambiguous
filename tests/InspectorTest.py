#!/usr/bin/python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous import decorator, is_self

from functools import wraps

class DecoratorTest(unittest.TestCase):

    # def test_is_self(self):
    #     class Foo():
    #         def foo(self):
    #             return is_self(Foo.foo, self)

    #         @classmethod
    #         def bar(cls):
    #             return is_self(Foo.bar, cls)

    #         @staticmethod
    #         def baz(arg):
    #             return is_self(Foo.baz, arg)


    #     self.assertTrue(Foo().foo())
    #     self.assertFalse(Foo().bar())
    #     self.assertFalse(Foo().baz('baz'))


    # def test_sanity(self):
    #     def func(arg):
    #         return is_self(func, arg)

    #     self.assertFalse(func('func'))


    def test_is_self_decorator(self):
        def check_self(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                return args and is_self(fn, args[0], check_self)
            return wrapper


        class Foo():
            @check_self
            def foo(self):
                pass

            @classmethod
            @check_self
            def bar(cls):
                pass

            @staticmethod
            @check_self
            def baz(arg):
                pass


        self.assertTrue(Foo().foo())
        # self.assertFalse(Foo().bar())
        # self.assertFalse(Foo().baz('baz'))


if __name__ == '__main__':
    unittest.main()
