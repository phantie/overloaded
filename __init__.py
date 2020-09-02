from functools import wraps
from typing import get_type_hints
from operator import attrgetter

def strict_types(f):
    hints = get_type_hints(f)
    def type_checker(*args, **kwargs):

        all_args = kwargs.copy()
        all_args.update(dict(zip(f.__code__.co_varnames, args)))

        for argument, argument_type in ((i, type(j)) for i, j in all_args.items()):
            if argument in hints:
                try:
                    issub = issubclass(argument_type, hints[argument])
                except TypeError as e:
                    if str(e) == "Subscripted generics cannot be used with class and instance checks":
                        pass
                    else: raise e
                else:
                    if not issub:
                        raise TypeError('Type of {} is {} and not {}'.format(argument, argument_type, hints[argument]))
        
        result = f(*args, **kwargs)

        if 'return' in hints and type(result) != hints['return']:
            raise TypeError('Type of result is {} and not {}'.format(type(result), hints['return']))

        return result

    type_checker.hintcount = len(hints)
    return type_checker


class FIterator:

    def __init__(self):
        self._store = []

    def append(self, f):
        self._store.append(f)

    def __call__(self, *args, **kwargs):
        idx = -1
        self._store.sort(reverse=True, key=attrgetter('hintcount'))
        while True:
            idx += 1

            try:
                result = self._store[idx](*args, **kwargs)
                return result

            except IndexError:
                raise TypeError("Function(s) exist(s) but with a different signature.")

            except (TypeError, NameError) as e:                
                if any(string in str(e) for string in ('Type of', 'missing', 'takes', 
                'not defined', 'unexpected', 'multiple')) and 'Type of result' not in str(e):
                    continue
                else:
                    raise e

    def __len__(self):
        return self._store.__len__()

class defaultnamespace:
    def __init__(self, _type):
        self._type = _type

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self.__setattr__(name, self._type())
            return object.__getattribute__(self, name)

class Overloader:
    store = defaultnamespace(FIterator)
    
    def __call__(self, f: callable):
        getattr(self.store, f.__name__).append(strict_types(f))
        return f

    def __getattribute__(self, name):

        if name != 'store' and (found := object.__getattribute__(object.__getattribute__(self, 'store'), name)):
            return found

        return object.__getattribute__(self, name)


overloaded = Overloader()


@overloaded
def foo(a, b): 
    print('Generic output', a, b)

@overloaded
def foo(a: str, b: str): 
    print('String' + a + b)

@overloaded
def foo(a: int, b: int): 
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



overloaded.foo('sup', 'dude')
overloaded.foo(100, 10)
overloaded.foo(1, 2, 3)
overloaded.foo(b=1, c=2, d=3)
overloaded.foo(1, 1, c = 1, d = 1)
overloaded.bar(2, 2)
overloaded.bar(2, 5, 5)

