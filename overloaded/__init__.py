from typing import get_type_hints, Union, Hashable, Type, Callable
from types import SimpleNamespace, FunctionType
from functools import partial
from inspect import isclass

from typeguard import typechecked


__all__ = ['Overloader']


def get_wrapper(f):
    res = type(f)
    return res if res is not FunctionType else None 


class WrappedIn:

    _registered = {}

    @classmethod
    def register(cls, 
        wrapper: Type, 
        get_callable,
        get_inner = lambda wrapped: wrapped.__func__ ):

        cls._registered[wrapper] = SimpleNamespace(
            get_callable=get_callable,
            get_inner=get_inner,
        )

    @classmethod
    def this(cls, wrapper):
        return wrapper in cls._registered

    def __class_getitem__(cls, key):
        return cls._registered[key]

    @classmethod
    def unwrap(cls, f):
        return cls[get_wrapper(f)].get_inner(f)

    @classmethod
    def get_name(cls, f):
        return cls.unwrap(f).__name__


def classmethod_get_callable(f, cls, *args, **kwargs):
    assert len(args) > 0, 'classmethod takes at least one argument - a class or instance of a class'
    
    cls_or_instance = args[0]
    args = args[1:]

    f = classmethod(f).__get__(cls_or_instance, cls)

    return lambda: f(*args, **kwargs)

def staticmethod_get_callable(f, cls, *args, **kwargs):
    f = staticmethod(f).__get__(None, cls)
    return lambda: f(*args, **kwargs)

def unwrapped_get_callable(f, cls, *args, **kwargs):
    return lambda: f(*args, **kwargs)


WrappedIn.register(classmethod, classmethod_get_callable)
WrappedIn.register(staticmethod, staticmethod_get_callable)
WrappedIn.register(None, unwrapped_get_callable, lambda f: f)


class Packed:

    sort_key = lambda value: value.hintcount
    sort_reverse = True

    def __init__(self, f: Callable, hintcount: int, original: Callable, id: Hashable, cls: Type = None, wrapper: Type = None):
        self.f = f
        self.hintcount = hintcount
        self.original = original
        self.id = id
        self.cls = cls
        self.wrapper = wrapper

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
            f = WrappedIn[package.wrapper].get_callable(package.f, package.cls, *args, **kwargs)
            try:
                return f()
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
                f = WrappedIn[self.package.wrapper].get_callable(
                    self.package.original if self.original else self.package.f,
                    self.package.cls,
                    *args, **kwargs)

                return f()


        assert id is not None, 'ID must not be None'

        for el in self._store:
            if el.id == id:
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


class Overloader:

    def __init__(self):
        self.store = defaultnamespace(lambda: Aggregate(Packed))
        self.clsstore = defaultnamespace(lambda: defaultnamespace(lambda: Aggregate(Packed)))
        self.tempmethods = []

    def method(self, f_or_id, id = None):
        if WrappedIn.this(get_wrapper(f_or_id)):
            self.tempmethods.append((f_or_id, id))
        else:
            return partial(self.method, id = f_or_id)

    def __call__(self, var: Union[Callable, Hashable]) -> Callable:
        def get_type_hint_count(f):
            return len(get_type_hints(f))

        def get_typechecked_f_and_hintcount(f):
            hintcount = get_type_hint_count(f)
            typechecked_f = typechecked(f, always=True)
            return typechecked_f, hintcount

        def process_f(f, id=None):
            typechecked_f, hintcount = get_typechecked_f_and_hintcount(f)
            self.store[f.__name__].add(typechecked_f, hintcount, f, id)
            return f

        def overload_class(cls):
            def process_meth(cls, f, id):
                wrapper = get_wrapper(f)
                unwrapped = WrappedIn.unwrap(f)

                typechecked_f, hintcount = get_typechecked_f_and_hintcount(unwrapped)
                self.clsstore[cls.__name__][unwrapped.__name__].add(typechecked_f, hintcount, unwrapped, id, cls, wrapper)

            for method, id in self.tempmethods:
                process_meth(cls, method, id)

            self.tempmethods.clear()

            return cls

        if isclass(var):
            return overload_class(var)
        elif callable(var):
            return process_f(var)
        else:
            return partial(process_f, id=var)

    def __getattribute__(self, name):
        if name in set(['store', 'clsstore', 'method', 'tempmethods']):
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