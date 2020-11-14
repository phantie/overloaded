class A:
    @classmethod
    def foo(cls): ...
    print(foo)
    print(dir(foo))
    print(foo.__func__)