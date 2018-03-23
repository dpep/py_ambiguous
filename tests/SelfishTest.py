#!/usr/bin/python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path
from ambiguous import selfish



class Foo():
    @selfish
    def itself(): return self


@selfish
class Bar():
    def itself(): return self

    @classmethod
    def classme(cls): return cls

    @staticmethod
    def static(): return globals().get('self')


# for test_globals()
global_self = 123

# for test_locals()
local_self = 123


class SelfishTest(unittest.TestCase):

    def test_basics(self):
        foo = Foo()
        self.assertEquals(foo, foo.itself())


    def test_class_wrapper(self):
        bar = Bar()
        self.assertEquals(bar, bar.itself())
        self.assertEquals(Bar, bar.classme())
        self.assertEquals(Bar, Bar.classme())
        self.assertEquals(None, bar.static())
        self.assertEquals(None, Bar.static())


    def test_name(fn_self):
        class Foo():
            @selfish(name='this')
            def this():
                with fn_self.assertRaises(NameError):
                    # undefined
                    self

                return this

        foo = Foo()
        fn_self.assertEquals(foo, foo.this())


    def test_closure(self):
        with self.assertRaises(ValueError):
            @selfish
            class Nope():
                # 'self' already bound from test_closure()
                def itself(): return self


    def test_wrapper(self):
        # ensure selfish methods are wrapped up properly

        self.assertEquals('Foo', Foo.__name__)

        self.assertEquals(
            '<unbound method Foo.itself>',
            str(Foo.itself)
        )
        self.assertEquals('itself', Foo.itself.__name__)


    def test_double_selfish(fn_self):
        @selfish
        class Foo():
            @selfish
            def itself(): return self

        foo = Foo()
        fn_self.assertEquals(foo, foo.itself())


    def test_globals(fn_self):
        fn_self.assertEquals(123, global_self)
        fn_self.assertNotIn('global_self', locals())

        @selfish(name='global_self')
        class Change():
            def do(val):
                globals()['global_self'] = val

        Change().do(789)

        # change to globals should persist
        fn_self.assertEquals(789, global_self)


    def test_locals(fn_self):
        local_self = 111

        fn_self.assertIn('local_self', locals())
        fn_self.assertIn('local_self', globals())
        fn_self.assertNotEquals(
            locals()['local_self'],
            globals()['local_self']
        )

        @selfish
        class Change():
            def do(val):
                # because it's not statically referenced, 'local_self'
                # in test_locals() isn't actually brought into
                # scope.  only the global one exists and it's been
                # overwritten by selfish

                fn_self.assertNotIn('local_self', locals())
                globals()['local_self'] = val

        Change().do(999)

        # local value should not have changed
        fn_self.assertEquals(111, local_self)

        # but the global one did
        fn_self.assertEquals(999, globals()['local_self'])



if __name__ == '__main__':
    unittest.main()