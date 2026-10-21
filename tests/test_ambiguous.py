import unittest

import ambiguous


class TestAmbiguous(unittest.TestCase):
    def test_basic(self):
        @ambiguous
        def foo():
            return True

        self.assertTrue(foo())
        self.assertTrue(foo)

        @ambiguous
        def bar():
            return "bar"

        self.assertEqual("bar", bar())
        self.assertEqual("bar", bar)

    def test_str_function(self):
        @ambiguous
        def foo(val=""):
            return f"foo{val}"

        self.assertEqual("foo", foo)
        self.assertEqual("foo", foo())

        self.assertEqual("fooboo", foo("boo"))
        self.assertEqual("fooboo", foo + "boo")

        self.assertEqual(3, len(foo))
        self.assertEqual(3, len(foo()))

        self.assertEqual("FOO", foo.upper())

        self.assertEqual("f", foo[0])
        self.assertEqual("oo", foo[1:])

        self.assertIsInstance(foo, str)
        self.assertIs(str, foo.__class__)

        self.assertEqual(str.__doc__, foo.__doc__)

    def test_list_function(self):
        @ambiguous
        def bar(val=None):
            return list(filter(None, [1, 2, 3] + [val]))

        self.assertEqual([1, 2, 3], bar)
        self.assertEqual([1, 2, 3], bar())

        self.assertEqual([1, 2, 3, 4], bar(4))
        self.assertEqual([1, 2, 3, 4], bar + [4])

        self.assertEqual(1, bar[0])
        self.assertEqual([2, 3], bar[1:])
        self.assertEqual([2, 3, 4], bar(4)[1:])

        self.assertEqual(3, len(bar))

        self.assertIsInstance(bar, list)

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
        data = {"a": 1, "b": 2}

        @ambiguous
        def baz(factor=1):
            return {k: v * factor for k, v in data.items()}

        self.assertEqual(data, baz)
        self.assertEqual(data, baz())

        self.assertEqual({"a": 2, "b": 4}, baz(2))

        self.assertEqual(1, baz["a"])
        self.assertIn(("a", 1), baz.items())
        self.assertEqual(18, baz(9)["b"])

        self.assertEqual(2, len(baz))

        self.assertIsInstance(baz, dict)

        # no exceptions here, and no persisted changes
        baz["a"] = 123
        self.assertEqual(1, baz["a"])

        del baz["a"]
        self.assertEqual(1, baz["a"])

    def test_unsupported_type(self):
        with self.assertRaises(TypeError):
            ambiguous(123)

    def test_inplace_ops(self):
        @ambiguous
        def num():
            return 10

        @ambiguous
        def letters():
            return "ab"

        # falls back to `x = x + y` rather than mutating the result
        x = num
        x += 1
        self.assertEqual(11, x)

        s = letters
        s += "c"
        self.assertEqual("abc", s)

    def test_truthiness(self):
        @ambiguous
        def text(val="x"):
            return val

        # str and list have no __bool__, so Python falls back to __len__
        self.assertTrue(text)
        self.assertFalse(text(""))
        self.assertFalse(not text)

    def test_mixed_type_ops(self):
        @ambiguous
        def one():
            return 1

        @ambiguous
        def also_one():
            return 1

        @ambiguous
        def letters():
            return "ab"

        # rely on Python's NotImplemented and reflected-op fallbacks
        self.assertEqual(one, 1.0)
        self.assertEqual(one, also_one)
        self.assertLess(one, 2.5)
        self.assertEqual(2.5, one + 1.5)
        self.assertEqual(2.5, 1.5 + one)
        self.assertEqual(1, max(one, 0.5))
        self.assertEqual("xab", "x" + letters)

    def test_counts(self):
        # don't call functions more than intended

        self.count = 0

        @ambiguous
        def inc():
            self.count += 1
            return self.count

        self.assertEqual(0, self.count)
        inc  # noqa: B018 -- this is inadvertently a no-op
        self.assertEqual(0, self.count)

        inc()  # must call explicitly to trigger
        self.assertEqual(1, self.count)

        res = 0 + inc  # or do something with the value
        self.assertEqual(2, res)
        self.assertEqual(2, self.count)

    def test_obj_from_function(self):
        class Foo:
            def __init__(self, name):
                self.name = name

            def get_name(self):
                return self.name

            def __call__(self):
                return "__call__"

            def __str__(self):
                return "__str__"

        @ambiguous
        def foo(name=""):
            return Foo(name)

        self.assertIsInstance(foo, Foo)
        self.assertIsInstance(foo(), Foo)
        self.assertEqual(Foo, foo.__class__)
        self.assertEqual("", foo.get_name())
        self.assertEqual("bob", foo("bob").get_name())
        self.assertEqual("__str__", str(foo))
        self.assertEqual("__call__", foo()())


if __name__ == "__main__":
    unittest.main()
