#!/usr/bin/env python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous import thing_or_things



@thing_or_things
def itself(args):
  return { x : x for x in args }


class TestThingOrThing(unittest.TestCase):

    def test_basics(self):
        self.assertEqual(3, itself(3))

        self.assertEqual({ 3 : 3 }, itself([ 3 ]))
        self.assertEqual({ 1 : 1, 2 : 2 }, itself([ 1, 2 ]))


    def test_default_arg(self):
        @thing_or_things
        def multiply(args, factor=1):
          return { x : x * factor for x in args }

        self.assertEqual(1, multiply(1))
        self.assertEqual(2, multiply(1, factor=2))
        self.assertEqual({ 1 : 1 }, multiply([ 1 ]))
        self.assertEqual({ 1 : 2, 2 : 4 }, multiply([ 1, 2 ], factor=2))


    def test_many_args(self):
        @thing_or_things('things')
        def math(factor, things, sub=1):
            return { x : x * factor - sub for x in things }

        self.assertEqual(9, math(10, 1))
        self.assertEqual(19, math(10, 2, 1))

        self.assertEqual(
            { 1 : 9, 2 : 19 },
            math(10, [1, 2], 1)
        )


    def test_kwargs(self):
        @thing_or_things
        def keywords(things, **kwargs):
            return { x : kwargs for x in things }

        self.assertEqual({}, keywords(1))
        self.assertEqual({'a' : 5}, keywords(1, a=5))


    def test_varargs(self):
        @thing_or_things('ids')
        def foo(ids, *args):
            return { x : [x] + list(args) for x in ids }

        self.assertEqual([1, 'a', 'b'], foo(1, 'a', 'b'))


    def test_empty(self):
        # this is fine
        self.assertEqual({}, itself([]))

        # but this doesn't make sense
        with self.assertRaises(TypeError):
            itself()


    def test_returns_none(self):
        # allowed to return None instead of list

        @thing_or_things
        def nope(things):
            return None

        self.assertIsNone(nope(1))
        self.assertIsNone(nope([ 1, 2, 3 ]))


    def test_arg_name(self):
        @thing_or_things('args')
        def prefix(prefix, args):
          return { x : "%s%s" % (prefix, x) for x in args }

        self.assertEqual('+1', prefix('+', 1))
        self.assertEqual({ 1 : '+1' }, prefix('+', [ 1 ]))
        self.assertEqual({ 1 : '+1', 2: '+2' }, prefix('+', [ 1, 2 ]))


    def test_arg_name_error(self):
        # use case makes no sense
        with self.assertRaises(TypeError):
            @thing_or_things
            def foo(): pass

        # ambiguous which arg is for things

        with self.assertRaises(TypeError):
            @thing_or_things
            def foo(x, y): pass

        with self.assertRaises(ValueError):
            @thing_or_things
            def foo(a, b, c=3): pass

        with self.assertRaises(ValueError):
            @thing_or_things
            def foo(a=1, b=2, c=3): pass

        # varargs are generally avoided

        with self.assertRaises(NotImplementedError):
            @thing_or_things
            def foo(*args): pass

        with self.assertRaises(NotImplementedError):
            @thing_or_things
            def foo(x, *args): pass

        with self.assertRaises(NotImplementedError):
            @thing_or_things('args')
            def foo(*args): pass


    def test_arg_error(self):
        @thing_or_things('things')
        def foo(a, things, c=3):
            return { thing : (a, thing, c) for thing in things }

        # too few args
        with self.assertRaises(TypeError):
            foo()

        with self.assertRaises(TypeError):
            foo(1)

        # too many args
        with self.assertRaises(TypeError):
            foo(1, 2, 3, 4)


    def test_obj_context(self):
        class Foo:
            @thing_or_things('args')
            def inst_it(self, args):
                assert isinstance(self, Foo)
                return { x : x for x in args }

            @classmethod
            @thing_or_things('args')
            def cls_it(cls, args):
                assert cls == Foo
                return { x : x for x in args }

            @staticmethod
            @thing_or_things
            def static_it(args):
                return { x : x for x in args }


        # instance method
        self.assertEqual(3, Foo().inst_it(3))
        self.assertEqual({ 3 : 3 }, Foo().inst_it([ 3 ]))

        # cls method
        self.assertEqual(3, Foo.cls_it(3))
        self.assertEqual({ 3 : 3 }, Foo.cls_it([ 3 ]))

        # static method
        self.assertEqual(3, Foo.static_it(3))
        self.assertEqual({ 3 : 3 }, Foo.static_it([ 3 ]))


    def test_types(self):
        self.assertEqual('a', itself('a'))
        self.assertEqual('abc', itself('abc'))
        self.assertEqual(u'abc', itself(u'abc'))
        self.assertEqual({ 'a' : 'a', 'b' : 'b' }, itself(['a', 'b']))
        self.assertEqual(1, itself(1))
        self.assertEqual(1.0, itself(1.0))


    def test_collection_types(self):
        # lists
        self.assertEqual({ 1 : 1 }, itself(list([ 1 ])))
        self.assertEqual({ 1 : 1, 2 : 2 }, itself(list([ 1, 2 ])))

        # tuples
        self.assertEqual({ 3 : 3 }, itself( (3, ) ))
        self.assertEqual({ 1 : 1, 2 : 2 }, itself( (1, 2) ))

        # sets
        self.assertEqual({ 3 : 3 }, itself(set([ 3 ])))
        self.assertEqual({ 1 : 1, 2 : 2 }, itself(set([ 1, 2 ])))


    def test_wrapper(self):
        # ensure function name was preserved
        self.assertEqual('itself', itself.__name__)

        class Foo:
            @thing_or_things
            def foo(self): pass

        self.assertEqual('foo', Foo.foo.__name__)


    def test_return_type(self):
        self.assertTrue(
            dict, type(
                thing_or_things(lambda things: {})([])
            )
        )

        with self.assertRaises(TypeError):
            thing_or_things(lambda things: 1)(1)

        with self.assertRaises(TypeError):
            thing_or_things(lambda things: True)(1)

        with self.assertRaises(TypeError):
            thing_or_things(lambda things: [])([1, 2])

        with self.assertRaises(TypeError):
            thing_or_things(lambda things: set())(1)


    def test_missing_key(self):
        with self.assertRaises(KeyError):
            thing_or_things(lambda things: {})(1)

        with self.assertRaises(KeyError):
            thing_or_things(lambda things: { 2 : 2 })(1)

        with self.assertRaises(KeyError):
            thing_or_things(lambda things: { 2 : 2 })([1, 2])


    def test_extra_key(self):
        with self.assertRaises(KeyError):
            thing_or_things(lambda things: { 1 : 1, 2 : 2 })(1)

        with self.assertRaises(KeyError):
            thing_or_things(lambda things: { 1 : 1 })([])



if __name__ == '__main__':
    unittest.main()
