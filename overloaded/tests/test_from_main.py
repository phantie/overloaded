from . import *


def test_borsch(overloaded: Overloader):
    @overloaded('useless')
    def foo(): return 0
  
    @overloaded('adder')
    def foo(a, b): return a + b
    
    @overloaded
    def foo(a: str, b: str): return '...'.join((a, b))

    @overloaded
    def foo(a: float, b: int): return int(a) + b
    
    assert overloaded.foo() == 0
    assert overloaded.foo(2, 2) == 4
    assert overloaded.foo('me', 'ow') == 'me...ow'
    assert overloaded.foo(2.5, 8) == 10

    assert overloaded.foo.with_id('useless')() == 0
    assert overloaded.foo.with_id('adder')(5, 5) == 10

    @overloaded
    class A:
        hidden = 42

        @overloaded.method('simple-method')
        def foo(self): return 'normal_foo_' + str(self.hidden)

        @overloaded.method('class-method')
        @classmethod
        def bar(cls): return 'classmethod_bar_' + str(cls.hidden)


        @overloaded.method
        @classmethod
        def bar(cls, v: str):
            return 'barbar' + v

        @overloaded.method('static-method')
        @staticmethod
        def baz(): return 'staticmethod_baz'

        @overloaded.method('another-sum')
        @staticmethod
        def sum(*args): return sum(args)



    a = A()
    a.hidden = 13

    assert overloaded.A.foo(a) == 'normal_foo_13'
    assert overloaded.A.foo.with_id('simple-method')(a) == 'normal_foo_13'
    assert overloaded.A.foo.with_id('simple-method')(self=a) == 'normal_foo_13'

    # That's how classmethod works
    assert overloaded.A.bar(A) == 'classmethod_bar_42' # Class
    assert overloaded.A.bar(a) == 'classmethod_bar_42' # Instance
    assert overloaded.A.bar.with_id('class-method')(A) == 'classmethod_bar_42'
    assert overloaded.A.bar.with_id('class-method')(a) == 'classmethod_bar_42'
    assert overloaded.A.bar.with_id('class-method')(cls=A) == 'classmethod_bar_42'
    assert overloaded.A.bar.with_id('class-method')(cls=a) == 'classmethod_bar_42'
    assert overloaded.A.bar(cls=A) == 'classmethod_bar_42'
    assert overloaded.A.bar(cls = A, v = 'bar') == 'barbarbar'

    assert overloaded.A.baz() == 'staticmethod_baz'
    assert overloaded.A.sum(1, 2, 3, 4) == 10
    assert overloaded.A.sum.with_id('another-sum')(1, 2, 3, 4) == 10

    assert overloaded.A.baz.with_id('static-method')() == 'staticmethod_baz'