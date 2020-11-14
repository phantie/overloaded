# overloaded
Polymorphism in python! May overload functions and methods (static- and classmethods included). Supports complex type hinting. Does not modify original functions, classes and methods.

All you need is an instance of Overloader:

    overloaded = Overloader()

Examples:

  With functions:
    
    @overloaded('useless') 
    def foo(): return 0
  
    @overloaded('adder') # NOTE You may use as ID any hashable type except classes and functions
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


  With methods:
    
    @overloaded
    class A:
        hidden = 42

        @overloaded.method('simple-method')
        def foo(self): return 'normal_foo_' + str(self.hidden)

        @overloaded.method
        @classmethod
        def bar(cls): return 'classmethod_bar_' + str(cls.hidden)

        @overloaded.method
        @staticmethod
        def baz(): return 'staticmethod_baz'

    a = A()
    a.hidden = 13

    assert overloaded.A.foo(a) == 'normal_foo_13'
    assert overloaded.A.foo.with_id('simple-method')(a)

    # That's how classmethod works
    assert overloaded.A.bar(A) == 'classmethod_bar_42' # Class
    assert overloaded.A.bar(a) == 'classmethod_bar_42' # Instance

    assert overloaded.A.baz() == 'staticmethod_baz'
