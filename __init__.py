from functools import wraps
import inspect

def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

class DetailedFunction:
    def __new__(cls, f):
        assert callable(f)
        return super().__new__(cls)

    def __init__(self, f):
        def get_unsetargs(args, defaults):
            for i, el in enumerate(args):
                if el in defaults:
                    edge = i
                    break
            else:
                edge = len(args)

            args = args[:edge]
            return args

        self.f = f
        code = f.__code__

        self.varnames = code.co_varnames

        self.argcount = code.co_argcount # a, /, b, *, c  NOTE: includes normail and positional-only args 
                                         # ^     ^     ^
        self.posonlyargcount = code.co_posonlyargcount # a, /, b, *, c
                                                       # ^
        self.kwonlyargcount = code.co_kwonlyargcount # a, /, b, *, c
                                                     #             ^
        self.defaultargs = get_default_args(f)
        self.unsetargs = get_unsetargs(self.varnames, self.defaultargs)

    def display(self):
        print(f"name: {self.f.__name__}")
        print(f"{self.varnames=}"[5:])
        print(f"{self.argcount=}"[5:])
        print(f"{self.posonlyargcount=}"[5:])
        print(f"{self.kwonlyargcount=}"[5:])
        print(f"{self.defaultargs=}"[5:])
        print(f"{self.unsetargs=}"[5:])

    
class FIterator:

    def __init__(self):
        self._store = []
        self._idx = -1

    def append(self, f):
        self._store.append(f)

    def __call__(self, *args, **kwargs):
        while 1:
            self._idx += 1

            try:
                result = self._store[self._idx](*args, **kwargs)
                self.reset()
                return result
            except IndexError:
                raise TypeError("Function(s) exist(s) but with a different signature.")
            except (TypeError, NameError) as e:
                if 'missing' in str(e) or 'takes' in str(e) or 'not defined' in str(e) or 'unexpected' in str(e) or 'multiple' in str(e):
                    continue
                else:
                    raise e
            else:
                break

    def reset(self):
        self._idx = -1

    def __len__(self):
        return self._store.__len__()

class defaultnamespace:
    def __init__(self, _type):
        self._type = _type
        self.attrs = []


    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            object.__getattribute__(object.__getattribute__(self, 'attrs'), 'append')(name)
            self.__setattr__(name, self._type())
            return object.__getattribute__(self, name)

    def display(self):
        for el in self.attrs:
            print(el, '=', len(getattr(self, el)))

class Overloader:
    store = defaultnamespace(FIterator)
    
    def __call__(self, f: callable):
        getattr(self.store, f.__name__).append(f)
        return f

    def __getattribute__(self, name):

        if name != 'store' and (found := object.__getattribute__(object.__getattribute__(self, 'store'), name)):
            return found

        return object.__getattribute__(self, name)



overloaded = Overloader()


@overloaded
def foo(a, b): 
    print(a + b)

@overloaded
def foo(a, b, c): 
    print(a - b - c)

@overloaded
def foo(b, c, d, k = 13):
    print(b / c / d + k)
 
@overloaded
def foo(b, a, /, c, d = 5): 
    print('a =', a, 'b =', b)

@overloaded
def bar(a, b):
    print(a * b, 'sup')

@overloaded
def bar(a, b, c):
    print(a * b * c, 'sup')

# overloaded.store.display()

overloaded.foo(100, 10)
overloaded.foo(1, 2, 3)
overloaded.foo(b=1, c=2, d=3)
overloaded.foo(1, 1, c = 1, d = 1)
overloaded.bar(2, 2)
overloaded.bar(2, 5, 5)

