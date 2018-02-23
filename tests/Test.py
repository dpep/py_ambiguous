#!/usr/bin/python

import os
import sys
import types
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

import ambiguous



class Test(unittest.TestCase):
    def test_str_function(self):
        @ambiguous.func
        def foo(val=''):
          return 'foo%s' % val

        self.assertEquals('foo', foo)
        self.assertEquals('foo', foo())

        self.assertEquals('fooboo', foo('boo'))
        self.assertEquals('fooboo', foo + 'boo')

        self.assertEquals(3, len(foo))
        self.assertEquals(3, len(foo()))

        self.assertEquals('FOO', foo.upper())

        self.assertEquals('f', foo[0])
        self.assertEquals('oo', foo[1:])

        self.assertTrue(isinstance(foo, str))
        self.assertTrue(issubclass(foo.__class__, str))

        # test __doc__


    def test_list_function(self):
        @ambiguous.func
        def bar(val=None):
          return filter(None, [ 1, 2, 3 ] + [ val ])

        self.assertEquals([ 1, 2, 3 ], bar)
        self.assertEquals([ 1, 2, 3 ], bar())

        self.assertEquals([ 1, 2, 3, 4 ], bar(4))
        self.assertEquals([ 1, 2, 3, 4 ], bar + [ 4 ])

        self.assertEquals(1, bar[0])
        self.assertEquals([ 2, 3 ], bar[1:])
        self.assertEquals([ 2, 3, 4 ], bar(4)[1:])

        self.assertEquals(3, len(bar))

        self.assertTrue(isinstance(bar, list))

        # no exceptions here
        bar[0] = 123
        del bar[0]


    def test_dict_function(self):
        data = { 'a' : 1, 'b' : 2, 'c' : 3 }

        @ambiguous.func
        def baz(key=None, value=None):
          return { k : v for k, v in dict(data, **{ key : value }).items() if k }

        self.assertEquals(data, baz)
        self.assertEquals(data, baz())

        self.assertEquals(dict(data, z=9), baz('z', 9))

        self.assertEquals(1, baz['a'])
        self.assertEquals(('a', 1), baz.items()[0])
        self.assertEquals(9, baz('z', 9)['z'])

        self.assertEquals(3, len(baz))

        self.assertTrue(isinstance(baz, dict))

        # no exceptions here
        baz['a'] = 123
        del baz['a']


    def test_obj_function(self):
        class Foo(object):
            def __init__(self, name=None):
                self.name = name
            def getName(self):
                return self.name or ''
            def __call__(self):
                return '__call__'
            def __str__(self):
                return '__str__'

        @ambiguous.func
        def foo(name=None):
            return Foo(name)


        self.assertTrue(isinstance(foo, Foo))
        self.assertTrue(isinstance(foo(), Foo))
        self.assertEquals('', foo.getName())
        self.assertEquals('bob', foo('bob').getName())
        self.assertEquals('__str__', str(foo))
        self.assertEquals('__call__', foo()())


    def test_object(self):
        class Foo(object):
            def __init__(self, name=''):
                self.name = name

            @ambiguous.instancemethod
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

        self.assertEquals('Foo().foo()', Foo().foo)
        self.assertEquals('Foo().foo()', Foo().foo())
        self.assertEquals('Foo(abc).foo()', Foo('abc').foo)
        self.assertEquals('Foo(abc).foo(xyz)', Foo('abc').foo('xyz'))


        # class methods
        self.assertEquals('%s.bar()' % Foo, Foo.bar)
        self.assertEquals('%s.bar()' % Foo, Foo.bar())
        self.assertEquals('%s.bar()' % Foo, Foo().bar())
        self.assertEquals('%s.bar(abc)' % Foo, Foo.bar('abc'))


        # static methods
        self.assertEquals('baz()', Foo.baz)
        self.assertEquals('baz()', Foo.baz())
        self.assertEquals('baz()', Foo().baz())
        self.assertEquals('baz(abc)', Foo.baz('abc'))



if __name__ == '__main__':
    unittest.main()
