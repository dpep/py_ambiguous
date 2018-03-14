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
        def abc(repeat=1):
            return 'abc' * repeat

        self.assertEquals('abc_abc', abc())
        self.assertEquals('abcabc_abc', abc(repeat=2))


    def test_kwargs(self):
        @suffix(str_='zzz')
        def xyz(repeat=1):
            return 'xyz' * repeat

        self.assertEquals('xyz_zzz', xyz())
        self.assertEquals('xyzxyz_zzz', xyz(2))


    def test_args(self):
        @suffix('123')
        def qqq():
            return 'qqq'

        self.assertEquals('qqq_123', qqq())


    def test_many_args(self):
        # basic decorator
        @prefix
        def pre():
            return 'pre'
        self.assertEquals('abc_pre', pre())

        # with a positional arg
        @prefix('123')
        def foo():
            return 'foo'
        self.assertEquals('123_foo', foo())

        # multiple args
        @prefix('456', 2)
        def bar():
            return 'bar'
        self.assertEquals('456_barbar', bar())

        # args and kwargs
        @prefix('789', repeat=3)
        def baz():
            return 'baz'
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



if __name__ == '__main__':
    unittest.main()
