from typeguard import typechecked
from operator import attrgetter
from functools import partial
from typing import get_type_hints, Union, Callable, Hashable

__all__ = ['Overloader']

class Packed:

    def __init__(self, f: Callable, hintcount: int, original: Callable, id: Hashable):
        self.f = f
        self.hintcount = hintcount
        self.original = original
        self.id = id

    sort_key = attrgetter("hintcount")
    sort_reverse = True

class Aggregate:    

    def __init__(self, _type):
        self._store = []
        self._type = _type

    def __call__(self, *args, **kwargs):

        self._store.sort(reverse=self._type.sort_reverse, key = self._type.sort_key)  
        
        for idx, package in enumerate(self._store):
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


    def __len__(self):
        return self._store.__len__()

    def add(self, *args, **kwargs):
        self._store.append(self._type(*args, **kwargs))

    def with_id(self, id, type_check=False) -> Callable:
        """On default returns the original function."""

        assert id is not None

        for el in self._store:
            if el.id == id:
                if type_check:
                    return el.f
                else:
                    return el.original

        else:
            raise KeyError(f'function with id {id} does not exist')
        

class defaultnamespace:

    def __init__(self, _get_inst):
        self._get_inst = _get_inst

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self.__setattr__(name, self._get_inst())
            return object.__getattribute__(self, name)

    def __getitem__(self, name):
        return self.__getattribute__(name)


class Overloader:

    def __init__(self):
        self.store = defaultnamespace(lambda: Aggregate(Packed))
    
    def __call__(self, var: Union[Callable, Hashable]) -> Callable:
        def process(f, id=None):
            def get_type_hint_count(f):
                return len(get_type_hints(f))

            hintcount = get_type_hint_count(f)
            typechecked_f = typechecked(f, always=True)

            self.store[f.__name__].add(typechecked_f, hintcount, f, id)
            return f

        if callable(var):
            return process(var)
        else:
            return partial(process, id=var)


    def __getattribute__(self, name):

        if name != 'store':
            return object.__getattribute__(object.__getattribute__(self, 'store'), name)

        return object.__getattribute__(self, name)