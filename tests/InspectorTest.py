#!/usr/bin/python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous.inspector import same_method


class InspectorTest(unittest.TestCase):

    def test_same_method(self):
        def foo(): pass
        def bar(): pass

        self.assertTrue(same_method(foo, foo))
        self.assertFalse(same_method(foo, bar))

        # check lamdas
        lambda1 = lambda: True
        lambda2 = lambda: True
        self.assertTrue(same_method(lambda1, lambda1))
        self.assertFalse(same_method(lambda1, lambda2))

        # same line number
        lambda1 = lambda: True; lambda2 = lambda: True
        self.assertTrue(same_method(lambda1, lambda1))
        self.assertFalse(same_method(lambda1, lambda2))

        # introspection
        self.assertTrue(same_method(same_method, same_method))

        # instance methods
        self.assertTrue(same_method(self.assertTrue, self.assertTrue))
        self.assertFalse(same_method(self.assertTrue, self.assertFalse))


if __name__ == '__main__':
    unittest.main()
