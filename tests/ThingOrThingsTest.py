#!/usr/bin/python

import os
import sys
import types
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
import ambiguous



@ambiguous.thing_or_things
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
        @ambiguous.thing_or_things
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
        @ambiguous.thing_or_things(offset=1)
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




if __name__ == '__main__':
    unittest.main()