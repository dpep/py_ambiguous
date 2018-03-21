#!/usr/bin/python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous import decorator



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


class DecoratorTest(unittest.TestCase):

    def test_basics(self):
        '''ensure basic wrapper function works'''

        @suffix
        def abc(repeat=1): return 'abc' * repeat

        self.assertEquals('abc_abc', abc())
        self.assertEquals('abcabc_abc', abc(repeat=2))

        # call decorator without args, ie. `suffix()` vs `suffix`
        @suffix()
        def xyz(): return 'xyz'
        self.assertEquals('xyz_abc', xyz())


    def test_kwargs(self):
        @suffix(str_='zzz')
        def xyz(repeat=1): return 'xyz' * repeat

        self.assertEquals('xyz_zzz', xyz())
        self.assertEquals('xyzxyz_zzz', xyz(2))


    def test_args(self):
        @suffix('123')
        def qqq(): return 'qqq'

        self.assertEquals('qqq_123', qqq())


    def test_many_args(self):
        # basic decorator
        @prefix
        def pre(): return 'pre'
        self.assertEquals('abc_pre', pre())

        # with a positional arg
        @prefix('123')
        def foo(): return 'foo'
        self.assertEquals('123_foo', foo())

        # multiple args
        @prefix('456', 2)
        def bar(): return 'bar'
        self.assertEquals('456_barbar', bar())

        # args and kwargs
        @prefix('789', repeat=3)
        def baz(): return 'baz'
        self.assertEquals('789_bazbazbaz', baz())


    def test_lambda(self):
        abc = lambda: 'abc'

        self.assertEquals('abc', abc())

        wrapped = suffix(abc)
        self.assertEquals('abc_abc', wrapped())

        self.assertEquals(
            'abc_abc',
            prefix(abc)(),
        )
        self.assertEquals(
            '123_abc',
            prefix(abc, '123')(),
        )
        self.assertEquals(
            '123_abcabc',
            prefix(abc, pre='123', repeat=2)(),
        )

        # out of order
        self.assertEquals(
            '123_abcabc',
            prefix(abc, repeat=2, pre='123')(),
        )


    def test_sequential_args(self):
        abc = lambda: 'abc'

        self.assertEquals(
            '123_abc',
            prefix('123')(abc)(),
        )
        self.assertEquals(
            '123_abcabc',
            prefix('123')(2)(abc)(),
        )
        self.assertEquals(
            '123_abcabc',
            prefix(pre='123')(repeat=2)(abc)(),
        )

        # out of order
        self.assertEquals(
            '123_abcabc',
            prefix(repeat=2)(pre='123')(abc)(),
        )

        self.assertEquals(
            '123_abcabc',
            prefix('123')(abc, repeat=2)(),
        )

        self.assertEquals(
            '123_abcabc',
            prefix(repeat=2)(abc, pre='123')(),
        )

        # passing kwarg, then args, then fn is ok
        self.assertEquals(
            '123_abcabc',
            prefix(repeat=2)('123')(abc)(),
        )

        # passing kwargs and then fn + args is ok
        self.assertEquals(
            '123_abcabc',
            prefix(repeat=2)(abc, '123')(),
        )

        # kwargs update
        self.assertEquals(
            '456_abcabc',
            prefix(pre='123', repeat=2)(abc, pre='456')(),
        )


    def test_errors(self):
        abc = lambda: 'abc'

        with self.assertRaises(ValueError):
            # arg order is ambiguous
            self.assertEquals(
                '123_abcabc',
                prefix('123')(abc, 2)(),
            )


    def test_wraps(self):
        self.assertEquals('suffix', suffix.__name__)

        @decorator
        def foo(): pass
        self.assertEquals('foo', foo.__name__)

        # test partials
        self.assertEquals('foo', foo().__name__)
        self.assertEquals('foo', foo(True).__name__)
        self.assertEquals('foo', foo(arg=123).__name__)


        @decorator
        def bar(fn, *args, **kwargs):
            def wrapper(*args):
                return fn(*args)
            return wrapper

        self.assertEquals('bar', bar.__name__)


        def baz(arg): pass
        self.assertEquals('baz', baz.__name__)
        self.assertEquals('baz', bar(baz).__name__)



if __name__ == '__main__':
    unittest.main()
