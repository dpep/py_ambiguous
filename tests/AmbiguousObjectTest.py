#!/usr/bin/env python

import os
import sys
import unittest

from types import *

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path

import ambiguous



class Test(unittest.TestCase):
    def test_basic(self):
        @ambiguous
        class Foo(object):
            def __init__(self, name=''):
                self.name = name

            def foo(self, val=''):
                return '%s.foo(%s)' % (self, val)

            @classmethod
            def bar(cls, val=''):
                return '%s.bar(%s)' % (cls, val)

            @staticmethod
            def baz(val=''):
                return 'baz(%s)' % val

            def __str__(self):
                return 'Foo(%s)' % self.name

        self.do(Foo)


    def test_helpers(self):
        class Foo(object):
            def __init__(self, name=''):
                self.name = name

            @ambiguous.method
            def foo(self, val=''):
                return '%s.foo(%s)' % (self, val)

            @ambiguous.classmethod
            def bar(cls, val=''):
                return '%s.bar(%s)' % (cls, val)

            @ambiguous.staticmethod
            def baz(val=''):
                return 'baz(%s)' % val

            def __str__(self):
                return 'Foo(%s)' % self.name

        self.do(Foo)


    def test_double_wrap(self):
        class Foo(object):
            def __init__(self, name=''):
                self.name = name

            # unfortunately, this helper is still needed
            @ambiguous.method
            def foo(self, val=''):
                return '%s.foo(%s)' % (self, val)

            @ambiguous
            @classmethod
            def bar(cls, val=''):
                return '%s.bar(%s)' % (cls, val)

            @ambiguous
            @staticmethod
            def baz(val=''):
                return 'baz(%s)' % val

            def __str__(self):
                return 'Foo(%s)' % self.name

        self.do(Foo)


    def do(self, Foo):
        self.assertTrue(isinstance(type, type(Foo)))
        self.assertEqual('Foo', Foo.__name__)
        self.assertTrue(isinstance(Foo.foo, FunctionType))

        with self.assertRaises(TypeError):
            # fails since method is unbound
            Foo.foo()

        self.assertEqual('Foo()', str(Foo()))

        self.assertEqual('Foo().foo()', Foo().foo)
        self.assertEqual('Foo().foo()', Foo().foo())
        self.assertEqual('Foo(abc).foo()', Foo('abc').foo)
        self.assertEqual('Foo(abc).foo(xyz)', Foo('abc').foo('xyz'))

        # class methods
        self.assertEqual('%s.bar()' % Foo, Foo.bar)
        self.assertEqual('%s.bar()' % Foo, Foo.bar())
        self.assertEqual('%s.bar()' % Foo, Foo().bar)
        self.assertEqual('%s.bar()' % Foo, Foo().bar())
        self.assertEqual('%s.bar()' % Foo, Foo('abc').bar)
        self.assertEqual('%s.bar(abc)' % Foo, Foo.bar('abc'))
        self.assertEqual('%s.bar(abc)' % Foo, Foo().bar('abc'))

        # static methods
        self.assertEqual('baz()', Foo.baz)
        self.assertEqual('baz()', Foo.baz())
        self.assertEqual('baz()', Foo().baz())
        self.assertEqual('baz(abc)', Foo.baz('abc'))
        self.assertEqual('baz(abc)', Foo().baz('abc'))



if __name__ == '__main__':
    unittest.main()
