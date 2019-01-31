#!/usr/bin/env python

import os
import sys
import types
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path

import ambiguous



class Test(unittest.TestCase):
    def test_basic(self):
        @ambiguous
        def foo():
          return True

        self.assertTrue(foo())
        self.assertTrue(foo)


    def test_str_function(self):
        @ambiguous
        def foo(val=''):
          return 'foo%s' % val

        self.assertEqual('foo', foo)
        self.assertEqual('foo', foo())

        self.assertEqual('fooboo', foo('boo'))
        self.assertEqual('fooboo', foo + 'boo')

        self.assertEqual(3, len(foo))
        self.assertEqual(3, len(foo()))

        self.assertEqual('FOO', foo.upper())

        self.assertEqual('f', foo[0])
        self.assertEqual('oo', foo[1:])

        self.assertTrue(isinstance(foo, str))
        self.assertTrue(issubclass(foo.__class__, str))

        self.assertEqual(str.__doc__, foo.__doc__)


    def test_list_function(self):
        @ambiguous
        def bar(val=None):
          return filter(None, [ 1, 2, 3 ] + [ val ])

        self.assertEqual([ 1, 2, 3 ], bar)
        self.assertEqual([ 1, 2, 3 ], bar())

        self.assertEqual([ 1, 2, 3, 4 ], bar(4))
        self.assertEqual([ 1, 2, 3, 4 ], bar + [ 4 ])

        self.assertEqual(1, bar[0])
        self.assertEqual([ 2, 3 ], bar[1:])
        self.assertEqual([ 2, 3, 4 ], bar(4)[1:])

        self.assertEqual(3, len(bar))

        self.assertTrue(isinstance(bar, list))

        # no exceptions here
        bar[0] = 123
        del bar[0]


    def test_dict_function(self):
        data = { 'a' : 1, 'b' : 2, 'c' : 3 }

        @ambiguous
        def baz(key=None, value=None):
          return { k : v for k, v in dict(data, **{ key : value }).items() if k }

        self.assertEqual(data, baz)
        self.assertEqual(data, baz())

        self.assertEqual(dict(data, z=9), baz('z', 9))

        self.assertEqual(1, baz['a'])
        self.assertEqual(('a', 1), baz.items()[0])
        self.assertEqual(9, baz('z', 9)['z'])

        self.assertEqual(3, len(baz))

        self.assertTrue(isinstance(baz, dict))

        # no exceptions here
        baz['a'] = 123
        del baz['a']


    def test_obj_function(self):
        class Foo(object):
            def __init__(self, name):
                self.name = name
            def getName(self):
                return self.name
            def __call__(self):
                return '__call__'
            def __str__(self):
                return '__str__'

        @ambiguous
        def foo(name=''):
            return Foo(name)


        self.assertTrue(isinstance(foo, Foo))
        self.assertTrue(isinstance(foo(), Foo))
        self.assertEqual('', foo.getName())
        self.assertEqual('bob', foo('bob').getName())
        self.assertEqual('__str__', str(foo))
        self.assertEqual('__call__', foo()())


    def test_object(self):
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


        # instance methods
        self.assertTrue(isinstance(Foo.foo, types.UnboundMethodType))

        with self.assertRaises(TypeError):
            # fails since method is unbound
            Foo.foo()

        self.assertEqual('Foo().foo()', Foo().foo)
        self.assertEqual('Foo().foo()', Foo().foo())
        self.assertEqual('Foo(abc).foo()', Foo('abc').foo)
        self.assertEqual('Foo(abc).foo(xyz)', Foo('abc').foo('xyz'))


        # class methods
        self.assertEqual('%s.bar()' % Foo, Foo.bar)
        self.assertEqual('%s.bar()' % Foo, Foo.bar())
        self.assertEqual('%s.bar()' % Foo, Foo().bar())
        self.assertEqual('%s.bar(abc)' % Foo, Foo.bar('abc'))


        # static methods
        self.assertEqual('baz()', Foo.baz)
        self.assertEqual('baz()', Foo.baz())
        self.assertEqual('baz()', Foo().baz())
        self.assertEqual('baz(abc)', Foo.baz('abc'))


    def test_old_obj(self):
        class Foo():
            def __str__(self):
                return '__str__'

        @ambiguous
        def foo():
            return Foo()

        # isinstance() does not work properly because type(Foo())
        # has type instance, so use __class__
        #   ie.  foo -> instance type -> class type
        self.assertEqual(Foo, foo.__class__.__class__)
        self.assertEqual('__str__', str(foo))


    def test_counts(self):
        """
        don't call functions more than intended
        """

        self.count = 0

        @ambiguous
        def inc():
            self.count += 1
            return self.count

        self.assertEqual(0, self.count)
        inc  # this is inadvertently a no-op
        self.assertEqual(0, self.count)

        inc()  # must call explicitly to trigger
        self.assertEqual(1, self.count)

        res = 0 + inc  # or do something with the value
        self.assertEqual(2, self.count)


    def test_module(self):
        @ambiguous
        def foo():
          return 'foo'

        self.assertEqual('foo', foo)
        self.assertEqual('foo', foo())



if __name__ == '__main__':
    unittest.main()
