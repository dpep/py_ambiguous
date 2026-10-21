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
      return 'foo'

    self.assertEqual('foo', foo)
    self.assertEqual('foo', foo())


  def test_dir(self):
    public = [ x for x in dir(ambiguous) if not x.startswith('__') ]
    self.assertEqual(sorted(ambiguous.__all__), public)


  def test_basic(self):
    @ambiguous
    class Foo(object):
      def __init__(self, name=''):
        self.name = name

      def foo(self, val=''):
        return '%s.foo(%s)' % (self, val)

      @classmethod
      def bar(cls, val=''):
        return '%s.bar(%s)' % (cls, val)

      @staticmethod
      def baz(val=''):
        return 'baz(%s)' % val

      def __str__(self):
        return 'Foo(%s)' % self.name

    self.do(Foo)


  def test_methods(self):
    # no class decorator needed: @ambiguous works on methods directly
    class Foo(object):
      def __init__(self, name=''):
        self.name = name

      @ambiguous
      def foo(self, val=''):
        return '%s.foo(%s)' % (self, val)

      @ambiguous
      @classmethod
      def bar(cls, val=''):
        return '%s.bar(%s)' % (cls, val)

      @ambiguous
      @staticmethod
      def baz(val=''):
        return 'baz(%s)' % val

      def __str__(self):
        return 'Foo(%s)' % self.name

    self.do(Foo)


  def test_falsy_instance(self):
    class Empty:
      def __len__(self):
        return 0

      @ambiguous
      def name(self):
        return 'empty'

    self.assertEqual('empty', Empty().name)
    self.assertEqual('empty', Empty().name())


  def test_subclass_classmethod(self):
    @ambiguous
    class A:
      @classmethod
      def who(cls):
        return cls.__name__

    class C:
      @ambiguous
      @classmethod
      def who(cls):
        return cls.__name__

    class B(A): pass
    class D(C): pass

    for Sub in (B, D):
      self.assertEqual(Sub.__name__, Sub.who)
      self.assertEqual(Sub.__name__, Sub.who())
      self.assertEqual(Sub.__name__, Sub().who())


  def test_class_attribute(self):
    @ambiguous
    def name(obj):
      return type(obj).__name__

    # like a plain function, an ambiguous function binds self
    class Foo:
      foo = name

    self.assertEqual('Foo', Foo().foo)


  def do(self, Foo):
    self.assertTrue(isinstance(type, type(Foo)))
    self.assertEqual('Foo', Foo.__name__)
    self.assertTrue(isinstance(Foo.foo, FunctionType))

    with self.assertRaises(TypeError):
      # fails since method is unbound
      Foo.foo()

    self.assertEqual('Foo()', str(Foo()))

    self.assertEqual('Foo().foo()', Foo().foo)
    self.assertEqual('Foo().foo()', Foo().foo())
    self.assertEqual('Foo(abc).foo()', Foo('abc').foo)
    self.assertEqual('Foo(abc).foo(xyz)', Foo('abc').foo('xyz'))

    # class methods
    self.assertEqual('%s.bar()' % Foo, Foo.bar)
    self.assertEqual('%s.bar()' % Foo, Foo.bar())
    self.assertEqual('%s.bar()' % Foo, Foo().bar)
    self.assertEqual('%s.bar()' % Foo, Foo().bar())
    self.assertEqual('%s.bar()' % Foo, Foo('abc').bar)
    self.assertEqual('%s.bar(abc)' % Foo, Foo.bar('abc'))
    self.assertEqual('%s.bar(abc)' % Foo, Foo().bar('abc'))

    # static methods
    self.assertEqual('baz()', Foo.baz)
    self.assertEqual('baz()', Foo.baz())
    self.assertEqual('baz()', Foo().baz())
    self.assertEqual('baz(abc)', Foo.baz('abc'))
    self.assertEqual('baz(abc)', Foo().baz('abc'))



if __name__ == '__main__':
  unittest.main()
