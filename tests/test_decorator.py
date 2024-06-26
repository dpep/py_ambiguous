#!/usr/bin/env python

import inspect
import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous import decorator


@decorator
def power(fn, exponent=2):
  return lambda x: fn(x) ** exponent


@decorator
def suffix(fn, str_='abc'):
  '''add a suffix to the result of the wrapped fn'''
  def wrapper(*args, **kwargs):
    return '%s_%s' % (fn(*args, **kwargs), str_)
  return wrapper

@decorator
def prefix(fn, pre='abc', repeat=1):
  '''prefix and repeat the result of the wrapped fn'''
  def wrapper(*args, **kwargs):
    return '%s_%s' % (
      pre,
      ''.join([ fn(*args, **kwargs) for i in range(repeat) ]),
    )
  return wrapper


class TestDecorator(unittest.TestCase):
  def test_basics(self):
    @power
    def squared(x): return x
    self.assertEqual(1, squared(1))
    self.assertEqual(4, squared(2))
    self.assertEqual(9, squared(3))


  def test_args(self):
    @power(3)
    def cubed(x): return x
    self.assertEqual(1, cubed(1))
    self.assertEqual(8, cubed(2))
    self.assertEqual(27, cubed(3))

    @power(exponent=4)
    def quad(x): return x
    self.assertEqual(1, quad(1))
    self.assertEqual(16, quad(2))
    self.assertEqual(81, quad(3))


  def test_empty_args(self):
    @power()
    def squared(x): return x

    self.assertEqual(1, squared(1))
    self.assertEqual(4, squared(2))
    self.assertEqual(9, squared(3))


  def test_strings(self):
    @suffix
    def abc(repeat=1): return 'abc' * repeat

    self.assertEqual('abc_abc', abc())
    self.assertEqual('abcabc_abc', abc(repeat=2))

    # call decorator without args, ie. `suffix()` vs `suffix`
    @suffix()
    def xyz(): return 'xyz'
    self.assertEqual('xyz_abc', xyz())


  def test_kwargs(self):
    @suffix(str_='zzz')
    def xyz(repeat=1): return 'xyz' * repeat

    self.assertEqual('xyz_zzz', xyz())
    self.assertEqual('xyzxyz_zzz', xyz(2))


  def test_many_args(self):
    # basic decorator
    @prefix
    def pre(): return 'pre'
    self.assertEqual('abc_pre', pre())

    # with a positional arg
    @prefix('123')
    def foo(): return 'foo'
    self.assertEqual('123_foo', foo())

    # multiple args
    @prefix('456', 2)
    def bar(): return 'bar'
    self.assertEqual('456_barbar', bar())

    # args and kwargs
    @prefix('789', repeat=3)
    def baz(): return 'baz'
    self.assertEqual('789_bazbazbaz', baz())


  def test_lambda(self):
    abc = lambda: 'abc'

    self.assertEqual('abc', abc())

    wrapped = suffix(abc)
    self.assertEqual('abc_abc', wrapped())

    self.assertEqual(
      'abc_abc',
      prefix(abc)(),
    )
    self.assertEqual(
      '123_abc',
      prefix(abc, '123')(),
    )
    self.assertEqual(
      '123_abcabc',
      prefix(abc, pre='123', repeat=2)(),
    )

    # out of order
    self.assertEqual(
      '123_abcabc',
      prefix(abc, repeat=2, pre='123')(),
    )


  def test_sequential_args(self):
    abc = lambda: 'abc'

    self.assertEqual(
      '123_abc',
      prefix('123')(abc)(),
    )
    self.assertEqual(
      '123_abcabc',
      prefix('123')(2)(abc)(),
    )
    self.assertEqual(
      '123_abcabc',
      prefix(pre='123')(repeat=2)(abc)(),
    )

    # out of order
    self.assertEqual(
      '123_abcabc',
      prefix(repeat=2)(pre='123')(abc)(),
    )

    self.assertEqual(
      '123_abcabc',
      prefix('123')(abc, repeat=2)(),
    )

    self.assertEqual(
      '123_abcabc',
      prefix(repeat=2)(abc, pre='123')(),
    )

    # passing kwarg, then args, then fn is ok
    self.assertEqual(
      '123_abcabc',
      prefix(repeat=2)('123')(abc)(),
    )

    # passing kwargs and then fn + args is ok
    self.assertEqual(
      '123_abcabc',
      prefix(repeat=2)(abc, '123')(),
    )

    # kwargs update
    self.assertEqual(
      '456_abcabc',
      prefix(pre='123', repeat=2)(abc, pre='456')(),
    )


  def test_errors(self):
    abc = lambda: 'abc'

    with self.assertRaises(ValueError):
      # arg order is ambiguous
      self.assertEqual(
        '123_abcabc',
        prefix('123')(abc, 2)(),
      )


  def test_wraps(self):
    @decorator
    def foo(fn): return fn
    self.assertEqual('foo', foo.__name__)

    # test partials
    self.assertEqual('foo', foo().__name__)
    self.assertEqual('foo', foo(True).__name__)
    self.assertEqual('foo', foo(arg=123).__name__)

    @foo
    def bar(): pass

    self.assertEqual('bar', bar.__name__)


  def test_obj(self):
    @decorator
    def double(fn):
      def wrapper(*args):
        return fn(*args) * 2
      return wrapper


    class Foo():
      def itself(self, val): return val

      @double
      def val(self, val): return val


    self.assertEqual(1, Foo().itself(1))
    self.assertEqual(2, double(Foo().itself)(1))

    self.assertEqual(2, Foo().val(1))


  def test_obj_wrapper(self):
    @decorator
    def itself(obj): return obj

    @itself
    class Foo():
      def one(self): return 1

    self.assertTrue(inspect.isclass(Foo))
    self.assertEqual('Foo', Foo.__name__)
    self.assertEqual('one', Foo.one.__name__)
    self.assertEqual(1, Foo().one())


    @decorator
    def upgrade(obj):
      klass = type('Upgrade', (obj,), {})
      klass.three = lambda self: 3
      return klass

    @upgrade
    class Bar(dict):
      def two(self): return 2

    self.assertEqual('Upgrade', Bar.__name__)
    self.assertTrue(issubclass(Bar, dict))
    self.assertEqual(2, Bar().two())
    self.assertEqual(3, Bar().three())


  def test_missing_arg(self):
    @decorator
    def mult(fn, factor): pass

    with self.assertRaises(TypeError):
      @mult
      def one(): pass


  def test_double_decorate(self):
    @decorator
    def double_that(fn):
      return lambda x: fn(x) * 2

    @double_that
    def double(x): return x

    self.assertEqual(2, double(1))
    self.assertEqual(4, double(2))

    quadruple = double_that(double)
    self.assertEqual(4, quadruple(1))
    self.assertEqual(8, quadruple(2))



if __name__ == '__main__':
  unittest.main()
