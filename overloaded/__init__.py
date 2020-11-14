from typeguard import typechecked
from operator import attrgetter
from functools import partial
from typing import get_type_hints, Union, Callable, Hashable, Type

from inspect import isclass

__all__ = ['Overloader']

class Packed:
    sort_key = attrgetter("hintcount")
    sort_reverse = True

    def __init__(self, f: Callable, hintcount: int, original: Callable, id: Hashable):
        self.f = f
        self.hintcount = hintcount
        self.original = original
        self.id = id

    def __str__(self):
        return f"{self.__class__.__name__}({self.f.__name__}, hintcount={self.hintcount}, id={self.id!r})"

    def __repr__(self):
        return str(self)

# class PackedCls:

#     def __init__(self, f: Callable, hintcount: int, original: Callable, id: Hashable):
#         self.f = f
#         self.hintcount = hintcount
#         self.original = original
#         self.id = id

#     sort_key = attrgetter("hintcount")
#     sort_reverse = True

class Aggregate:    

    def __init__(self, _type):
        print('Created new')
        self._store = []
        self._type = _type

    def __call__(self, *args, **kwargs):

        self._store.sort(reverse=self._type.sort_reverse, key = self._type.sort_key)  
        
        for package in self._store:
            try:
                return package.f(*args, **kwargs)

            except TypeError as error:
                typechecked_error_messages_beginnings = [
                    "too many positional arguments",
                    "missing a required argument",
                    "got an unexpected keyword argument",
                    "type of argument",
                ]
                
                strerror = str(error)
                if any(strerror.startswith(beginning) for beginning in typechecked_error_messages_beginnings):
                    continue
                else:
                    raise error
        else:
            if len(self._store) > 1:
                error_msg = "functions exist, but with the different signatures"
            else:
                error_msg = "function exists, but with a different signature"

            raise TypeError(error_msg)

    def __str__(self):
        return f"{self.__class__.__name__}({self._store})"

    def __len__(self):
        return self._store.__len__()

    def add(self, *args, **kwargs):
        self._store.append(self._type(*args, **kwargs))

    def with_id(self, id, type_check=False) -> Callable:
        """On default returns the original function."""

        assert id is not None
        # print(dir(self._store))
        # print(list(el.id for el in self._store))
        print(self._store)
        for el in self._store:

            if el.id == id:
                if type_check:
                    return el.f
                else:
                    return el.original

        else:
            raise KeyError(f'function with id {id!r} does not exist')
        

class defaultnamespace:

    def __init__(self, _get_inst):
        self._get_inst = _get_inst

    def __getattr__(self, name):
        setattr(self, name, self._get_inst())
        return getattr(self, name)

    def __getitem__(self, name):
        return getattr(self, name)

    def __str__(self):
        return '{' + ', '.join(f'"{k}": {v}' for k, v in vars(self).items() if not k.startswith('_')) + '}'


class Overloader:

    class method:
        # counter = 0

        def __new__(cls, f_or_id, id = None):
            if callable(f_or_id):
                return super().__new__(cls)
            else:
                # cls.counter += 1
                return partial(cls, id = f_or_id)

        def __init__(self, f_or_id: Union[Callable, Hashable], id = None):
            # f_or_id.__name__ = f"{f_or_id.__name__}|{self.counter}"
 
            self.f = f_or_id
            self.id = id
            print(self.f, self.id)


        def unwrap(self):
            return self.f

    def __init__(self):
        self.store = defaultnamespace(lambda: Aggregate(Packed))
        self.clsstore = defaultnamespace(lambda: defaultnamespace(lambda: Aggregate(Packed)))
    
    def __call__(self, var: Union[Callable, Hashable]) -> Callable:
        def get_type_hint_count(f):
            return len(get_type_hints(f))

        def process_f(f, id=None):

            hintcount = get_type_hint_count(f)
            typechecked_f = typechecked(f, always=True)

            self.store[f.__name__].add(typechecked_f, hintcount, f, id)
            return f


        def overload_class(cls):
            def process_meth(classname, meth_ovl):
                print('called')
                f = meth_ovl.unwrap()
                id = meth_ovl.id
                hintcount = get_type_hint_count(f)
                typechecked_f = typechecked(f, always=True)
                self.clsstore[classname][f.__name__].add(typechecked_f, hintcount, f, id)
                print(self.clsstore)


            # def process_cls(cls, meth_ovl):
            #     f = meth_ovl.unwrap()
            #     id = meth_ovl.id
            #     hintcount = get_type_hint_count(f)
            #     typechecked_f = typechecked(f, always=True)
            #     self.clsstore[cls.__name__][f.__name__].add(typechecked_f, hintcount, f, id)
            #     print(self.clsstore)

            classname = cls.__name__
            print(len(vars(cls).items()))
            print(len(list(v for v in vars(cls).values() if isinstance(v, self.method))))
            for key, value in vars(cls).items():
                if isinstance(value, self.method):
                    print('must process', key)
                    # clsname = cls.__name__
                    f = value.f
                    # fname = f.__name__

                    setattr(cls, key, value.unwrap())
                    process_meth(classname, value)
            return cls

        if isclass(var):
            return overload_class(var)
        elif callable(var):
            return process_f(var)
        else:
            return partial(process_f, id=var)

    def __getattribute__(self, name):
        # if name == 'method':
        #     return object.__getattribute__(self, name)

        if name in set(['store', 'clsstore', 'method']):
            return object.__getattribute__(self, name)
        else:
            try:
                return object.__getattribute__(object.__getattribute__(self, 'store'), name)
            except AttributeError:
                return object.__getattribute__(object.__getattribute__(self, 'clsstore'), name)



overloaded = Overloader()



@overloaded
class A:
    @overloaded.method('primary')
    def foo(self, one): return one

    @overloaded.method('secondary')
    def foo(self, one, two): return one + two

    @overloaded.method('3')
    def foo(self, one, two, three): return one + two + three


    # @overloaded.method('secondary')
    # def bar(self, plus): return 'bar' + plus

print(dir(A))

a = A()



# print(overloaded.A.bar.with_id('secondary')(a, 'baz'))
# print(overloaded.A.foo.with_id('primary')(a))

# print(overloaded.A.foo(a, 1, 2, 3))
# print(overloaded.A.foo(a, 1, 2, 3))
# print(overloaded.A.foo.with_id('3')(a, 1, 2, 3))

# @overloaded(13)
# def foo():...

# @overloaded(14)
# def foo(a):...

# overloaded.foo.with_id(13)

# class B:
#     def foo(self): ...
#     def bar(self): ...

# nsp = defaultnamespace(lambda: defaultnamespace(lambda: Aggregate(Packed)))

# nsp['B'].