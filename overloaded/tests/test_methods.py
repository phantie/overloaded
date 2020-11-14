from . import *

# overloaded

def test_basic(overloaded):
    @overloaded
    class A:
        @overloaded.method
        def foo(self):
            return 'foo'

        @overloaded.method
        def bar(self):
            return 'bar'

    a = A()

    assert overloaded.A.foo(a) == 'foo'
    assert overloaded.A.bar(a) == 'bar'


# def test_with_id(overloaded):
    # @overloaded
    # class A:
    #     @overloaded.method('primary')
    #     def foo(self):
    #         return 'primary_foo'

    #     @overloaded.method('secondary')
    #     def foo(self):
    #         return 'secondary_foo'

    # a = A()

    # assert overloaded.A.foo.with_id('primary')(a) == 'primary_foo'
    # assert overloaded.A.foo.with_id('secondary')(a) == 'secondary_foo'

    # @overloaded
    # class A:
    #     @overloaded.method('primary')
    #     def foo(self): return 'foo'

    #     # @overloaded.method('secondary')
    #     # def foo(self): return 'foo'

    # a = A()

    # assert overloaded.A.foo.with_id('primary')(a) == 'foo'
