#!/usr/bin/python

import os
import sys
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

        # no exceptions here
        baz['a'] = 123
        del baz['a']



if __name__ == '__main__':
    unittest.main()
