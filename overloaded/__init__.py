from typeguard import typechecked
from operator import attrgetter
from functools import partial
from typing import get_type_hints, Union, Callable, Hashable, Type

from inspect import isclass

__all__ = ['Overloader']

class Packed:
    sort_key = attrgetter("hintcount")
    sort_reverse = True

    def __init__(self, f: Callable, hintcount: int, original: Callable, id: Hashable, cls: Type = None):
        self.f = f
        self.hintcount = hintcount
        self.original = original
        self.id = id
        self.cls = cls

    def __str__(self):
        name = getattr(self.f, '__name__', None) or getattr(self.f.__func__, '__name__')
        return f"{self.__class__.__name__}({name!r}, hintcount={self.hintcount}, id={self.id!r})"

    def __repr__(self):
        return str(self)

    def prepare_callable(self, f, *args, **kwargs):
        if is_classmethod(f):
            assert len(args) > 0, 'classmethod takes at least one argument - a class or instance of a class'
            
            cls_or_instance = args[0]

            args = args[1:]
        
            f = f.__get__(cls_or_instance, self.cls)

        elif is_staticmethod(f):
            f = f.__get__(None, self.cls)
        
        return f, args, kwargs

def is_staticmethod(f):
    return isinstance(f, staticmethod)

def is_classmethod(f):
    return isinstance(f, classmethod)

def is_static_or_classmethod(f):
    return is_staticmethod(f) or is_classmethod(f)

class Aggregate:    

    def __init__(self, _type):
        self._store = []
        self._type = _type

    def __call__(self, *args, **kwargs):

        self._store.sort(reverse=self._type.sort_reverse, key = self._type.sort_key)  
        
        for package in self._store:
            f, _args, _kwargs = package.prepare_callable(package.f, *args, **kwargs)

            try:
                return f(*_args, **_kwargs)

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
        class Proxy:
            def __init__(self, package, original):
                self.package = package
                self.original = original

            def __call__(self, *args, **kwargs):
                f, _args, _kwargs = self.package.prepare_callable(
                    self.package.original if self.original else self.package.f,
                     *args, **kwargs)

                return f(*_args, **_kwargs)


        assert id is not None, 'ID must not be None'

        for el in self._store:

            if el.id == id:
                if type_check:
                    f = el.f
                else:
                    f = el.original

                if is_static_or_classmethod(f):
                    f = Proxy(el, not type_check)

                return f
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


def unwrap_method(f):
    if is_static_or_classmethod(f):
        return f.__func__
    else:
        return f

class Overloader:

    class meth_wrap:
        def __init__(self, f: Union[Callable, Hashable], id = None):
            self.f = f
            self.id = id

        def unwrap(self):
            return self.f

    def method(self, f_or_id, id = None):
        if callable(f_or_id) or is_static_or_classmethod(f_or_id):
            self.tempmethods.append(self.meth_wrap(f_or_id, id = id))
        else:
            return partial(self.method, id = f_or_id)

    def __init__(self):
        self.store = defaultnamespace(lambda: Aggregate(Packed))
        self.clsstore = defaultnamespace(lambda: defaultnamespace(lambda: Aggregate(Packed)))
        self.tempmethods = []

    def __call__(self, var: Union[Callable, Hashable]) -> Callable:
        def get_type_hint_count(f):
            return len(get_type_hints(unwrap_method(f)))

        def get_typechecked_f_and_hintcount(f):
            hintcount = get_type_hint_count(f)

            typechecked_f = typechecked(unwrap_method(f), always=True)

            if isinstance(f, staticmethod):
                typechecked_f = staticmethod(typechecked_f)
            elif isinstance(f, classmethod):
                typechecked_f = classmethod(typechecked_f)

            return typechecked_f, hintcount

        def process_f(f, id=None):
            typechecked_f, hintcount = get_typechecked_f_and_hintcount(f)
            self.store[f.__name__].add(typechecked_f, hintcount, f, id)
            return f

        def overload_class(cls):
            def process_meth(cls, meth_ovl):
                id = meth_ovl.id

                f = meth_ovl.unwrap()
                typechecked_f, hintcount = get_typechecked_f_and_hintcount(f)
                self.clsstore[cls.__name__][unwrap_method(f).__name__].add(typechecked_f, hintcount, f, id, cls)

            for method in self.tempmethods:
                process_meth(cls, method)

            self.tempmethods.clear()

            return cls

        if isclass(var):
            return overload_class(var)
        elif callable(var):
            return process_f(var)
        else:
            return partial(process_f, id=var)

    def __getattribute__(self, name):
        if name in set(['store', 'clsstore', 'meth_wrap', 'method', 'tempmethods']):
            return object.__getattribute__(self, name)
        else:
            try:
                return object.__getattribute__(object.__getattribute__(self, 'store'), name)
            except AttributeError:
                try:
                    return object.__getattribute__(object.__getattribute__(self, 'clsstore'), name)
                except AttributeError as e:
                    if str(e).startswith("'defaultnamespace' object has no attribute"):
                        raise AttributeError(f'Class "{name}" has no overloaded methods')
                    else:
                        raise