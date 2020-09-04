from overloaded import Overloader
import pytest
import sys
from numbers import Number

@pytest.fixture
def overloaded():
    return Overloader()

def test_raises_attr_error_if_function_not_overloaded(overloaded):
    def foo(): ...
    
    with pytest.raises(AttributeError):
        overloaded.foo()

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
    assert overloaded.foo(set()) == 'generic:set()'

def test_specific_over_generic_advanced(overloaded):
    @overloaded
    def foo(a, b, c): return '||'

    @overloaded
    def foo(a: str, b: int, c: tuple): return 'str|int|tuple'
    
    @overloaded
    def foo(a: str, b, c: tuple): return 'str||tuple'

    assert overloaded.foo('', 0, (3, 4)) == 'str|int|tuple'
    assert overloaded.foo('', set(), (3, 4)) == 'str||tuple'
    assert overloaded.foo(0, -1, 0) == '||'

def test_with_different_kinds_of_args(overloaded):
    

    @overloaded
    def foo(a: Number, b: Number, c: Number): return a + b - c

    assert not overloaded.foo(1, 1, 2) 
    assert not overloaded.foo(1, 1, c = 2) 
    assert not overloaded.foo(1, b = 1, c = 2)
    assert not overloaded.foo(a = 1.5, b = 1.5, c = 3)

    @overloaded
    def foo(a: Number, /, b: Number, c: Number, *, d: Number): return a - b + c - d

    assert not overloaded.foo(2.5, 5, 7.5, d = 5)
    assert not overloaded.foo(2.5, 5, c = 7.5, d = 5)
    with pytest.raises(TypeError):
        overloaded.foo(2.5, 5, 7.5, 5)


def test_does_not_change_original(overloaded):
    def foo(): ...
    _foo = foo
    foo = overloaded(foo)

    assert foo is _foo
    assert not hasattr(foo, 'hintcount')


def test_complicated_types(overloaded):

    from typing import Type, List, Dict

    if sys.version_info >= (3, 9):
        List = list
        Dict = dict


    @overloaded
    def foo(_type: Type[set]): return _type

    assert overloaded.foo(set) is set


    @overloaded
    def foo(_type: set): return _type

    assert isinstance(overloaded.foo(set()), set)


    @overloaded
    def bar(arr: List[Dict]): return arr
    assert overloaded.bar([{1: 2, 3: 4}, {5: 6}])
    
    with pytest.raises(TypeError):
        overloaded.bar([[], []])


def test_parameterized(overloaded):
    @overloaded('1')
    def foo(): ...



    assert overloaded.foo() is None
    assert foo() is None

def test_param_id(overloaded):
    @overloaded(13)
    def foo(a: Number): return a ** 2

    @overloaded
    def foo(a: Number): return a ** 3

    @overloaded(42)
    def foo(): return 0

    @overloaded((4, 9, 2020))
    def foo(): return "The day this test was written"

    assert foo() == "The day this test was written"
    assert overloaded.foo.with_id(13)(3) == 9
    assert overloaded.foo.with_id(42)() == 0
    assert overloaded.foo.with_id((4, 9, 2020))() == "The day this test was written"


    with pytest.raises(KeyError):
        overloaded.foo.with_id('some id')


def test_does_not_change_original_parameterized(overloaded):
    def bar(): ...
    _bar = bar
    bar = overloaded('random_id')(bar)
    assert bar is _bar
    assert not hasattr(bar, 'hintcount')