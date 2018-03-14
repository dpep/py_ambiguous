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


class DecoratorTest(unittest.TestCase):

    def test_basics(self):
        '''ensure basic wrapper function works'''

        @suffix
        def abc(repeat=1):
            return 'abc' * repeat

        self.assertEquals('abc_abc', abc())
        self.assertEquals('abcabc_abc', abc(repeat=2))


    def test_decorator_kwargs(self):
        @suffix(str_='zzz')
        def xyz(repeat=1):
            return 'xyz' * repeat

        self.assertEquals('xyz_zzz', xyz())
        self.assertEquals('xyzxyz_zzz', xyz(2))



if __name__ == '__main__':
    unittest.main()
