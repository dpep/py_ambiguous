import abc
import asyncio
import dataclasses
import inspect
import pydoc
import time
import unittest
from types import FunctionType, ModuleType

import ambiguous


class TestAmbiguousObject(unittest.TestCase):
    def test_module_is_callable(self):
        # the module is made callable so it can be used directly as a
        # decorator, eg. `import ambiguous; @ambiguous`
        self.assertTrue(callable(ambiguous))
        self.assertIsInstance(ambiguous, ModuleType)

        @ambiguous
        def foo():
            return "foo"

        self.assertEqual("foo", foo)
        self.assertEqual("foo", foo())

    def test_dir(self):
        public = [x for x in dir(ambiguous) if not x.startswith("__")]
        self.assertEqual(sorted(ambiguous.__all__), public)

    def test_basic(self):
        @ambiguous
        class Foo:
            def __init__(self, name=""):
                self.name = name

            def foo(self, val=""):
                return f"{self}.foo({val})"

            @classmethod
            def bar(cls, val=""):
                return f"{cls}.bar({val})"

            @staticmethod
            def baz(val=""):
                return f"baz({val})"

            def __str__(self):
                return f"Foo({self.name})"

        self.assert_methods(Foo)

    def test_methods(self):
        # no class decorator needed: @ambiguous works on methods directly
        class Foo:
            def __init__(self, name=""):
                self.name = name

            @ambiguous
            def foo(self, val=""):
                return f"{self}.foo({val})"

            @ambiguous
            @classmethod
            def bar(cls, val=""):
                return f"{cls}.bar({val})"

            @ambiguous
            @staticmethod
            def baz(val=""):
                return f"baz({val})"

            def __str__(self):
                return f"Foo({self.name})"

        self.assert_methods(Foo)

    def test_falsy_instance(self):
        class Empty:
            def __len__(self):
                return 0

            @ambiguous
            def name(self):
                return "empty"

        self.assertEqual("empty", Empty().name)
        self.assertEqual("empty", Empty().name())

    def test_subclass_classmethod(self):
        @ambiguous
        class A:
            @classmethod
            def who(cls):
                return cls.__name__

        class B(A):
            pass

        self.assertEqual("B", B.who)
        self.assertEqual("B", B.who())
        self.assertEqual("B", B().who())

    def test_async_methods_skipped(self):
        @ambiguous
        class Service:
            async def fetch(self):
                return "data"

            @classmethod
            async def create(cls):
                return cls()

            async def stream(self):
                yield "data"

            def name(self):
                return "service"

        # async methods stay awaitable and detectable as async
        self.assertTrue(inspect.iscoroutinefunction(Service().fetch))
        self.assertTrue(inspect.iscoroutinefunction(Service.create))
        self.assertTrue(inspect.isasyncgenfunction(Service().stream))
        self.assertEqual("data", asyncio.run(Service().fetch()))
        self.assertEqual("service", Service().name)

    def test_async_rejected(self):
        # can't be awaited without the call, so parentheses aren't optional
        with self.assertRaisesRegex(TypeError, "async"):

            @ambiguous
            async def fetch():
                return "data"

        with self.assertRaisesRegex(TypeError, "async"):

            class Service:
                @ambiguous
                @classmethod
                async def create(cls):
                    return cls()

    def test_class_decorator_other_attrs(self):
        class Lazy:
            # eg. a werkzeug LocalProxy outside an app context
            def __getattr__(self, name):
                raise RuntimeError("outside app context")

        @ambiguous
        def now():
            raise AssertionError("called while decorating")

        @ambiguous
        class Foo:
            app = Lazy()
            clock = now

            def name(self):
                return "foo"

        self.assertEqual("foo", Foo().name)

    def test_class_attribute(self):
        @ambiguous
        def region():
            return "us-east-1"

        # assigned rather than defined in the class body, it stays a value
        class Foo:
            default = region

        @dataclasses.dataclass
        class Settings:
            zone: str = region

        self.assertEqual("us-east-1", Foo.default)
        self.assertEqual("us-east-1", Foo().default)
        self.assertEqual("us-east-1", Settings().zone)

    def test_class_attribute_no_rebinding(self):
        # like plain Python, builtins and already-bound methods don't bind self
        class Foo:
            @ambiguous
            def name(self):
                return "foo"

        class Bar:
            now = ambiguous(time.time)
            stolen = Foo().name

        self.assertIsInstance(Bar().now, float)
        self.assertEqual("foo", Bar().stolen)

    def test_class_introspection(self):
        # abc, dataclasses and pydoc read the class namespace directly, which
        # must not call the method without self
        class Base(abc.ABC):
            @abc.abstractmethod
            def kind(self): ...

            @ambiguous
            def name(self):
                return "base"

        class Impl(Base):
            def kind(self):
                return "impl"

        @dataclasses.dataclass
        class Data:
            x: int = 1

            @ambiguous
            def name(self):
                return "data"

        @dataclasses.dataclass
        @ambiguous
        class Decorated:
            x: int = 1

            def name(self):
                return "decorated"

        self.assertEqual("base", Impl().name)
        self.assertEqual("data", Data().name)
        self.assertEqual("decorated", Decorated().name)
        self.assertIn("name", pydoc.render_doc(Data))

    def test_abstract_methods(self):
        class Base(abc.ABC):
            @ambiguous
            @abc.abstractmethod
            def kind(self): ...

            @ambiguous
            @classmethod
            @abc.abstractmethod
            def label(cls): ...

        class Impl(Base):
            @ambiguous
            def kind(self):
                return "impl"

            @ambiguous
            @classmethod
            def label(cls):
                return "Impl"

        self.assertEqual({"kind", "label"}, Base.__abstractmethods__)
        with self.assertRaises(TypeError):
            Base()

        self.assertEqual("impl", Impl().kind)
        self.assertEqual("Impl", Impl.label)

    def test_signature(self):
        @ambiguous
        def foo():
            return "foo"

        # the proxy itself, not the method-descriptor path for builtins
        self.assertEqual("(*args, **kwargs)", str(inspect.signature(foo)))

    def assert_methods(self, Foo):
        self.assertIsInstance(Foo, type)
        self.assertEqual("Foo", Foo.__name__)
        self.assertIsInstance(Foo.foo, FunctionType)

        with self.assertRaises(TypeError):
            # fails since method is unbound
            Foo.foo()

        self.assertEqual("Foo()", str(Foo()))

        self.assertEqual("Foo().foo()", Foo().foo)
        self.assertEqual("Foo().foo()", Foo().foo())
        self.assertEqual("Foo(abc).foo()", Foo("abc").foo)
        self.assertEqual("Foo(abc).foo(xyz)", Foo("abc").foo("xyz"))

        # class methods
        self.assertEqual(f"{Foo}.bar()", Foo.bar)
        self.assertEqual(f"{Foo}.bar()", Foo.bar())
        self.assertEqual(f"{Foo}.bar()", Foo().bar)
        self.assertEqual(f"{Foo}.bar()", Foo().bar())
        self.assertEqual(f"{Foo}.bar()", Foo("abc").bar)
        self.assertEqual(f"{Foo}.bar(abc)", Foo.bar("abc"))
        self.assertEqual(f"{Foo}.bar(abc)", Foo().bar("abc"))

        # static methods
        self.assertEqual("baz()", Foo.baz)
        self.assertEqual("baz()", Foo.baz())
        self.assertEqual("baz()", Foo().baz())
        self.assertEqual("baz(abc)", Foo.baz("abc"))
        self.assertEqual("baz(abc)", Foo().baz("abc"))


if __name__ == "__main__":
    unittest.main()
