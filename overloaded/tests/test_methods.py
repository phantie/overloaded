from . import *


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

def test_classmethod(overloaded):
    @overloaded
    class A:
        @overloaded.method
        @classmethod
        def foo(cls):
            return 'awesome'

        @overloaded.method
        @classmethod
        def foo(cls, what):
            return f'superb-{what}'

        @overloaded.method
        @classmethod
        def bar(cls, yo):
            return 'heyo' + yo

    @overloaded
    class B:
        @overloaded.method
        @classmethod
        def baz(cls, *args):
            return sum(args)

        @overloaded.method
        @classmethod
        def bring(cls, *stuff, for_whom = 'him'):
            return f'Bring {for_whom} {" and ".join(stuff)}'

    a = A()
    b = B()

    assert overloaded.A.foo(A) == 'awesome'
    assert overloaded.A.foo(a) == 'awesome'

    assert overloaded.A.bar(a, 'mayo') == 'heyomayo'
    assert overloaded.A.bar(A, 'mayo') == 'heyomayo'

    assert overloaded.B.baz(b, 1, 2, 3) == 6
    assert overloaded.B.baz(B, 1, 2, 3) == 6

    assert overloaded.B.bring(b, 'shoes', 'booze', for_whom='me') == 'Bring me shoes and booze'


def test_staticmethod(overloaded):
    @overloaded
    class A:
        @overloaded.method
        @staticmethod
        def foo():
            return 'awesome'

        @overloaded.method
        @staticmethod
        def foo(what):
            return f'superb-{what}'

    @overloaded
    class B:
        @overloaded.method
        @staticmethod
        def foo(a, b, c):
            return a + b + c

        @overloaded.method
        @staticmethod
        def foo(a, b):
            return a + b

    assert overloaded.A.foo() == 'awesome'
    assert overloaded.A.foo('man') == 'superb-man'

    assert overloaded.B.foo(2, 2) == 4
    assert overloaded.B.foo(1, 1, 1) == 3

def test_raises_Attribute_error_if_class_is_not_Overloaded(overloaded):
    with pytest.raises(AttributeError) as err:
        overloaded.A.foo()

    assert str(err.value) == 'Class "A" has no overloaded methods'

    with pytest.raises(AttributeError) as err:
        @overloaded
        class A: ...

        overloaded.A.foo()
    
    assert str(err.value) == 'Class "A" has no overloaded methods'

def test_keyword_arguments(overloaded):
    @overloaded
    class A:
        from typing import List

        @overloaded.method
        def foo(self, i: int):
            return 2 * i

        @overloaded.method
        def foo(self, i: List[int]):
            return [el*2 for el in i]


        secret = 8

        @overloaded.method
        @classmethod
        def bar(cls, a: int, b: int) -> int:
            return a * b * cls.secret

        @overloaded.method
        @classmethod
        def bar(cls, a: float, b: float) -> int:
            return round(a * b) * cls.secret


        from typing import Dict
        from numbers import Real
        

        @overloaded.method
        @staticmethod
        def baz(**kwargs):
            return [k * v for k, v in kwargs.items()]

        @overloaded.method
        @staticmethod
        def baz(r: Real):
            from math import pi
            return pi * r ** 2

    a = A()

    assert overloaded.A.foo(self=a, i=2) == 4
    assert overloaded.A.foo(self=a, i=[1, 2, 3]) == [2, 4, 6]

    assert overloaded.A.bar(cls=A, a=1, b=2) == 16
    assert overloaded.A.bar(cls=a, a=2, b=2) == 32
    assert overloaded.A.bar(cls=A, a=2.25, b=2) == 32
    assert overloaded.A.bar(cls=A, a=2.26, b=2) == 40

    assert overloaded.A.baz(me=3, mo=3, you=0) == ['mememe', 'momomo', '']
    assert 314 < overloaded.A.baz(r=10) < 315 