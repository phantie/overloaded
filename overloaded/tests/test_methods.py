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


def test_with_id(overloaded):
    @overloaded
    class A:
        @overloaded.method('primary')
        def foo(self):
            return 'primary_foo'

        @overloaded.method('secondary')
        def foo(self):
            return 'secondary_foo'
        
        @overloaded.method('finally')
        def foo(self):
            return 'finally_foo'

    a = A()

    assert overloaded.A.foo.with_id('primary')(a) == 'primary_foo'
    assert overloaded.A.foo.with_id('secondary')(a) == 'secondary_foo'
    assert overloaded.A.foo.with_id('finally')(a) == 'finally_foo'

def test_raises_AttributeError_if_class_not_overloaded(overloaded):
    with pytest.raises(AttributeError):
        overloaded.A.foo

def test_multiple_oveloaded_classes(overloaded):
    @overloaded
    class A:
        @overloaded.method
        def foo(self):
            return 'A_foo'

        @overloaded.method
        def bar(self, what):
            return f"A_bar{what}"

    @overloaded
    class B:
        @overloaded.method
        def bar(self):
            return 'B_bar'

        @overloaded.method
        def foo(self, what):
            return f"B_foo{what}"

        @overloaded.method
        def bar(self, what):
            return f'B_bar{what}'

    a = A()
    b = B()

    assert overloaded.A.foo(a) == 'A_foo'
    assert overloaded.A.bar(a, '_baz') == 'A_bar_baz'

    assert overloaded.B.bar(b) == 'B_bar'
    assert overloaded.B.bar(b, '_baz') == 'B_bar_baz'
    assert overloaded.B.foo(b, '_baz') == 'B_foo_baz'

def test_ok_if_no_overloaded_methods(overloaded):
    @overloaded
    class A: ...

    @overloaded
    class B: ...

# def test_classmethod(overloaded):
#     @overloaded
#     class A:
#         @overloaded.method
#         @classmethod
#         def foo(cls):
#             return 'awesome'

#         @overloaded.method
#         @classmethod
#         def foo(cls, what):
#             return f'superb-{what}'

#     assert overloaded.A.foo(A) == 'awesome'
        
# def test_staticmethod(overloaded):
#     @overloaded
#     class A:
#         @overloaded.method
#         @staticmethod
#         def foo():
#             return 'awesome'

#         @overloaded.method
#         @staticmethod
#         def foo(what):
#             return f'superb-{what}'

#     assert overloaded.A.foo() == 'awesome'
        