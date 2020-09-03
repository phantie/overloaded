import pytest
from overloaded import Overloader

@pytest.fixture
def overloaded():
    return Overloader()

def test_basic_same_function_name(overloaded):
    @overloaded
    def foo(a, b): return a ** b

    assert overloaded.foo(2, 3) == 8
    assert overloaded.foo(1, 3) == 1

def test_overloading_basic_same_function_name(overloaded):
    @overloaded
    def foo(a, b): return sum((a, b))
    
    @overloaded
    def foo(a, b, c): return sum((a, b, c))

    assert overloaded.foo(9, 33) == 42
    assert overloaded.foo(3, 33, 333) == 369

def test_overloading_different_functions_same_arguments(overloaded):
    @overloaded
    def foo(a): return a ** 2

    @overloaded
    def bar(a): return a ** 3

    assert overloaded.foo(3) == 9
    assert overloaded.bar(3) == 27

def test_specific_over_generic(overloaded):
    @overloaded
    def foo(a: str): return 'str:' + a

    @overloaded
    def foo(a: float): return 'float:' + str(a)

    @overloaded
    def foo(a): return 'generic:' + str(a)

    assert overloaded.foo('ing') == 'str:ing'
    assert overloaded.foo(3.14) == 'float:3.14'
    assert overloaded.foo(0) == 'generic:0'

def test_specific_over_generic_advanced(overloaded):
    class A: ...

    @overloaded
    def foo(a, b, c): return '||'

    @overloaded
    def foo(a: str, b: int, c: tuple): return 'str|int|tuple'
    
    @overloaded
    def foo(a: str, b, c: tuple): return 'str||tuple'

    assert overloaded.foo('', 0, (3, 4)) == 'str|int|tuple'
    assert overloaded.foo('', A(), (3, 4)) == 'str||tuple'
    assert overloaded.foo(0, -1, 0) == '||'


def test_does_not_change_original_function(overloaded):
    def foo(): ...
    _foo = foo
    foo = overloaded(foo)

    assert foo is _foo
