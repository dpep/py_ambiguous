#!/usr/bin/python

import os
import sys
import types
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous import thing_or_things



@thing_or_things
def itself(args):
  return { x : x for x in args }


class ThingOrThingTest(unittest.TestCase):

    def test_basics(self):
        self.assertEquals(3, itself(3))
        self.assertEquals(3, itself(*[ 3 ]))

        self.assertEquals({ 3 : 3 }, itself([ 3 ]))
        self.assertEquals({ 1 : 1, 2 : 2 }, itself(1, 2))
        self.assertEquals({ 1 : 1, 2 : 2 }, itself([ 1, 2 ]))
        self.assertEquals({ 1 : 1, 2 : 2 }, itself(*[ 1, 2 ]))


    def test_types(self):
        self.assertEquals('a', itself('a'))
        self.assertEquals('abc', itself('abc'))
        self.assertEquals({ 'a' : 'a', 'b' : 'b' }, itself('a', 'b'))
        self.assertEquals(1.0, itself(1.0))


    def test_empty(self):
        self.assertEquals({}, itself())
        self.assertEquals({}, itself([]))
        self.assertEquals({}, itself(*[]))


    def test_collection_types(self):
        # lists
        self.assertEquals({ 1 : 1 }, itself(list([ 1 ])))
        self.assertEquals({ 1 : 1, 2 : 2 }, itself(list([ 1, 2 ])))

        # tuples
        self.assertEquals(3, itself((3)))
        self.assertEquals({ 3 : 3 }, itself((3, )))
        self.assertEquals({ 1 : 1, 2 : 2 }, itself( (1, 2) ))

        # sets
        self.assertEquals({ 3 : 3 }, itself(set([ 3 ])))
        self.assertEquals({ 1 : 1, 2 : 2 }, itself(set([ 1, 2 ])))


    def test_param(self):
        @thing_or_things
        def multiply(args, factor=1):
          return { x : x * factor for x in args }

        self.assertEquals(1, multiply(1))
        self.assertEquals(2, multiply(1, factor=2))
        self.assertEquals({ 1 : 2 }, multiply([ 1 ], factor=2))

        self.assertEquals({ 1 : 1, 2 : 2 }, multiply(1, 2))
        self.assertEquals({ 1 : 2, 2 : 4 }, multiply(1, 2, factor=2))
        self.assertEquals({ 1 : 2, 2 : 4 }, multiply([ 1, 2 ], factor=2))
        self.assertEquals({ 1 : 2, 2 : 4 }, multiply(*[ 1, 2 ], factor=2))


    def test_prefix(self):
        @thing_or_things(offset=1)
        def prefix(prefix, args):
          return { x : "%s%s" % (prefix, x) for x in args }

        # empty args
        self.assertEquals({}, prefix('+'))

        self.assertEquals('+1', prefix('+', 1))
        self.assertEquals({ 1 : '+1' }, prefix('+', [ 1 ]))
        self.assertEquals({ 1 : '+1', 2: '+2' }, prefix('+', 1, 2))
        self.assertEquals({ 1 : '+1', 2: '+2' }, prefix('+', [ 1, 2 ]))
        self.assertEquals({ 1 : '+1', 2: '+2' }, prefix('+', *[ 1, 2 ]))

        with self.assertRaises(ValueError):
            # missing prefix param
            prefix()


    def test_obj_context(self):
        class Foo:
            @thing_or_things(offset=1)
            def inst_it(self, args):
                assert isinstance(self, Foo)
                return { x : x for x in args }

            @classmethod
            @thing_or_things(offset=1)
            def cls_it(cls, args):
                assert cls == Foo
                return { x : x for x in args }

            @staticmethod
            @thing_or_things
            def static_it(args):
                return { x : x for x in args }


        # instance method
        self.assertEquals(3, Foo().inst_it(3))
        self.assertEquals({ 3 : 3 }, Foo().inst_it([ 3 ]))
        self.assertEquals({ 1 : 1, 2 : 2 }, Foo().inst_it(1, 2))

        # cls method
        self.assertEquals(3, Foo.cls_it(3))
        self.assertEquals({ 3 : 3 }, Foo.cls_it([ 3 ]))
        self.assertEquals({ 1 : 1, 2 : 2 }, Foo.cls_it(1, 2))

        # static method
        self.assertEquals(3, Foo.static_it(3))
        self.assertEquals({ 3 : 3 }, Foo.static_it([ 3 ]))
        self.assertEquals({ 1 : 1, 2 : 2 }, Foo.static_it(1, 2))


if __name__ == '__main__':
    unittest.main()
