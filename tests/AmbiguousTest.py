#!/usr/bin/env python

import os
import sys
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

        @ambiguous
        def bar():
          return 'bar'

        self.assertEqual('bar', bar())
        self.assertEqual('bar', bar)


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
          return list(filter(None, [ 1, 2, 3 ] + [ val ]))

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

        # although the update doesn't stick
        self.assertEqual(1, bar[0])

        # unless you save the returned object
        res = bar()
        res[0] = 123
        self.assertEqual(123, res[0])


    def test_dict_function(self):
        data = { 'a' : 1, 'b' : 2 }

        @ambiguous
        def baz(factor=1):
          return { k : v * factor for k, v in data.items() }

        self.assertEqual(data, baz)
        self.assertEqual(data, baz())

        self.assertEqual({ 'a' : 2, 'b' : 4 }, baz(2))

        self.assertEqual(1, baz['a'])
        self.assertTrue(('a', 1) in baz.items())
        self.assertEqual(18, baz(9)['b'])

        self.assertEqual(2, len(baz))

        self.assertTrue(isinstance(baz, dict))

        # no exceptions here, and no persisted changes
        baz['a'] = 123
        self.assertEqual(1, baz['a'])

        del baz['a']
        self.assertEqual(1, baz['a'])


    def test_counts(self):
        # don't call functions more than intended

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
        self.assertEqual(2, res)
        self.assertEqual(2, self.count)


    def test_obj_from_function(self):
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


    def test_old_obj_from_func(self):
        class Foo():
            def __str__(self):
                return '__str__'

        @ambiguous
        def foo():
            return Foo()

        self.assertEqual('__str__', str(foo))

        # isinstance() does not work properly because type(Foo())
        # has type 'instance', so use __class__
        if sys.version_info[0] == 2:
            #   ie.  foo -> instance type -> class type
            self.assertEqual(Foo, foo.__class__.__class__)
        else:
            # Python3 fixed this quirk so Class.__class__ works as expected
            self.assertEqual(Foo, foo.__class__)




if __name__ == '__main__':
    unittest.main()
