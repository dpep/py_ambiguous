import unittest

from ambiguous import thing_or_things


@thing_or_things
def itself(args):
    return {x: x for x in args}


class TestThingOrThing(unittest.TestCase):
    def test_basics(self):
        self.assertEqual(3, itself(3))

        self.assertEqual({3: 3}, itself([3]))
        self.assertEqual({1: 1, 2: 2}, itself([1, 2]))

    def test_default_arg(self):
        @thing_or_things
        def multiply(args, factor=1):
            return {x: x * factor for x in args}

        self.assertEqual(1, multiply(1))
        self.assertEqual(2, multiply(1, factor=2))
        self.assertEqual({1: 1}, multiply([1]))
        self.assertEqual({1: 2, 2: 4}, multiply([1, 2], factor=2))

    def test_many_args(self):
        @thing_or_things("things")
        def math(factor, things, sub=1):
            return {x: x * factor - sub for x in things}

        self.assertEqual(9, math(10, 1))
        self.assertEqual(19, math(10, 2, 1))

        self.assertEqual({1: 9, 2: 19}, math(10, [1, 2], 1))

    def test_thing_by_keyword(self):
        self.assertEqual(1, itself(args=1))
        self.assertEqual({1: 1, 2: 2}, itself(args=[1, 2]))

    def test_thing_default(self):
        @thing_or_things("things")
        def defaulted(things=(1,)):
            return {x: x for x in things}

        self.assertEqual({1: 1}, defaulted())
        self.assertEqual(2, defaulted(2))

    def test_kwargs(self):
        @thing_or_things
        def keywords(things, **kwargs):
            return {x: kwargs for x in things}

        self.assertEqual({}, keywords(1))
        self.assertEqual({"a": 5}, keywords(1, a=5))

    def test_varargs(self):
        @thing_or_things("ids")
        def foo(ids, *args):
            return {x: [x] + list(args) for x in ids}

        self.assertEqual([1, "a", "b"], foo(1, "a", "b"))

    def test_keyword_only(self):
        @thing_or_things
        def kwonly(*, things):
            return {x: x for x in things}

        @thing_or_things("things")
        def named(prefix, *, things):
            return {x: f"{prefix}{x}" for x in things}

        # positional params still win when not named explicitly
        @thing_or_things
        def keyed(things, *, key):
            return {x: key(x) for x in things}

        self.assertEqual(1, kwonly(things=1))
        self.assertEqual({1: 1, 2: 2}, kwonly(things=[1, 2]))
        self.assertEqual("+1", named("+", things=1))
        self.assertEqual(2, keyed(1, key=lambda x: x * 2))

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
        self.assertIsNone(nope([1, 2, 3]))

    def test_arg_name(self):
        @thing_or_things("args")
        def prefix(prefix, args):
            return {x: f"{prefix}{x}" for x in args}

        self.assertEqual("+1", prefix("+", 1))
        self.assertEqual({1: "+1"}, prefix("+", [1]))
        self.assertEqual({1: "+1", 2: "+2"}, prefix("+", [1, 2]))

    def test_arg_name_error(self):
        # use case makes no sense
        with self.assertRaises(TypeError):

            @thing_or_things
            def foo():
                pass

        # ambiguous which arg is for things

        with self.assertRaisesRegex(ValueError, r"@thing_or_things\('x'\)"):

            @thing_or_things
            def foo(x, y):
                pass

        with self.assertRaises(ValueError):

            @thing_or_things
            def foo(a, b, c=3):
                pass

        with self.assertRaises(ValueError):

            @thing_or_things
            def foo(a=1, b=2, c=3):
                pass

        # varargs are generally avoided

        with self.assertRaises(NotImplementedError):

            @thing_or_things
            def foo(*args):
                pass

        with self.assertRaises(NotImplementedError):

            @thing_or_things
            def foo(x, *args):
                pass

        with self.assertRaises(NotImplementedError):

            @thing_or_things("args")
            def foo(*args):
                pass

    def test_unknown_arg_name(self):
        with self.assertRaisesRegex(ValueError, "foo.. has no parameter 'thing'"):

            @thing_or_things("thing")
            def foo(things):
                pass

        with self.assertRaisesRegex(NotImplementedError, r"\*\*kw can't be the thing"):

            @thing_or_things("kw")
            def foo(things, **kw):
                pass

    def test_methods(self):
        # self / cls is never the thing
        class Repo:
            @thing_or_things
            def get(self, ids):
                return {x: x for x in ids}

            @thing_or_things
            def kwonly(self, *, ids):
                return {x: x for x in ids}

        self.assertEqual(1, Repo().get(1))
        self.assertEqual({1: 1}, Repo().get([1]))
        self.assertEqual(1, Repo().kwonly(ids=1))

    def test_self_param_on_function(self):
        # outside a class, a param named cls is just a param
        @thing_or_things
        def css(cls, prefix="x-"):
            return {c: prefix + c for c in cls}

        self.assertEqual("x-btn", css("btn"))

    def test_method_hint(self):
        # name the method by its qualname, and suggest the thing, not self
        with self.assertRaisesRegex(
            ValueError, r"Foo\.get\(\).*@thing_or_things\('ids'\)"
        ):

            class Foo:
                @thing_or_things
                def get(self, ids, keys):
                    pass

    def test_async(self):
        with self.assertRaisesRegex(TypeError, "async"):

            @thing_or_things
            async def get(ids):
                return {}

    def test_nameless_callable(self):
        class Getter:
            def __call__(self, things):
                return [1]

        # errors name the callable even without a __name__
        with self.assertRaisesRegex(TypeError, "Getter.*must return a dict"):
            thing_or_things(Getter())(0)

    def test_arg_error(self):
        @thing_or_things("things")
        def foo(a, things, c=3):
            return {thing: (a, thing, c) for thing in things}

        # too few args
        with self.assertRaises(TypeError):
            foo()

        with self.assertRaises(TypeError):
            foo(1)

        # too many args
        with self.assertRaises(TypeError):
            foo(1, 2, 3, 4)

        # bad calls never reach the function
        called = []

        @thing_or_things
        def spy(things):
            called.append(things)
            return {x: x for x in things}

        with self.assertRaises(TypeError):
            spy()

        self.assertEqual([], called)

    def test_obj_context(self):
        # record self / cls in a list rather than assert, which -O strips
        seen = []

        class Foo:
            @thing_or_things("args")
            def inst_it(self, args):
                seen.append(self)
                return {x: x for x in args}

            @classmethod
            @thing_or_things("args")
            def cls_it(cls, args):
                seen.append(cls)
                return {x: x for x in args}

            @staticmethod
            @thing_or_things
            def static_it(args):
                return {x: x for x in args}

        # instance method
        foo = Foo()
        self.assertEqual(3, foo.inst_it(3))
        self.assertEqual({3: 3}, foo.inst_it([3]))
        self.assertEqual([foo, foo], seen)
        seen.clear()

        # cls method
        self.assertEqual(3, Foo.cls_it(3))
        self.assertEqual({3: 3}, Foo.cls_it([3]))
        self.assertEqual([Foo, Foo], seen)

        # static method
        self.assertEqual(3, Foo.static_it(3))
        self.assertEqual({3: 3}, Foo.static_it([3]))

    def test_types(self):
        self.assertEqual("a", itself("a"))
        self.assertEqual("abc", itself("abc"))
        self.assertEqual({"a": "a", "b": "b"}, itself(["a", "b"]))
        self.assertEqual(1, itself(1))
        self.assertEqual(1.0, itself(1.0))

    def test_collection_types(self):
        # lists
        self.assertEqual({1: 1}, itself([1]))
        self.assertEqual({1: 1, 2: 2}, itself([1, 2]))

        # tuples
        self.assertEqual({3: 3}, itself((3,)))
        self.assertEqual({1: 1, 2: 2}, itself((1, 2)))

        # sets
        self.assertEqual({3: 3}, itself({3}))
        self.assertEqual({1: 1, 2: 2}, itself({1, 2}))

        # frozensets
        self.assertEqual({1: 1, 2: 2}, itself(frozenset({1, 2})))

    def test_wrapper(self):
        # ensure function name was preserved
        self.assertEqual("itself", itself.__name__)

        class Foo:
            @thing_or_things
            def foo(self):
                pass

        self.assertEqual("foo", Foo.foo.__name__)

    def test_return_type(self):
        self.assertEqual({}, thing_or_things(lambda things: {})([]))

        with self.assertRaisesRegex(TypeError, "must return a dict or None, got int"):
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

        with self.assertRaisesRegex(KeyError, r"missing things: \[1\]"):
            thing_or_things(lambda things: {2: 2})(1)

        with self.assertRaises(KeyError):
            thing_or_things(lambda things: {2: 2})([1, 2])

    def test_unhashable_thing(self):
        called = []

        @thing_or_things
        def spy(things):
            called.append(things)
            return {}

        with self.assertRaisesRegex(TypeError, "spy.*unhashable"):
            spy({1: 2})

        self.assertEqual([], called)

    def test_key_order(self):
        # listed in the order of the things, not set order
        with self.assertRaisesRegex(KeyError, r"missing things: \[3, 1, 2\]"):
            thing_or_things(lambda things: {})([3, 1, 2])

        with self.assertRaisesRegex(KeyError, r"extra keys: \['z', 'y'\]"):
            thing_or_things(lambda things: {1: 1, "z": 0, "y": 0})(1)

    def test_extra_key(self):
        with self.assertRaisesRegex(KeyError, r"extra keys: \[2\]"):
            thing_or_things(lambda things: {1: 1, 2: 2})(1)

        with self.assertRaises(KeyError):
            thing_or_things(lambda things: {1: 1})([])


if __name__ == "__main__":
    unittest.main()
