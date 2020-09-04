from operator import attrgetter
from functools import wraps
from typeguard import typechecked
from typing import get_type_hints
from collections import namedtuple
from copy import deepcopy

__all__ = ['Overloader']

class IteratorOverListOfFunctions:

    def __init__(self):
        self._store = []

    def __call__(self, *args, **kwargs):
        idx = -1
        self._store.sort(reverse=True, key = lambda x: x[1])  
        while True:
            idx += 1

            try:
                return self._store[idx].f(*args, **kwargs)

            except IndexError:
                if idx > 1:
                    error_msg = "Functions exist but with the different signatures."
                else:
                    error_msg = "Function exists but with a different signature."
                
                raise TypeError(error_msg)

            except TypeError as e: # hard debugging because it catches all the TypeErrors. TOFIX
                continue

    def __len__(self):
        return self._store.__len__()

    def add(self, f):
        self._store.append(f)

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
    fmt = namedtuple('fmt', ['f', 'hintcount', 'original', 'id'])

    def __init__(self):
        self.store = defaultnamespace(IteratorOverListOfFunctions)
    
    def __call__(self, f: callable):
        def get_type_hint_count(f):
            return len(get_type_hints(f))

        hintcount = get_type_hint_count(f)
        typechecked_f = typechecked(f, always=True)

        data = self.fmt(typechecked_f, hintcount, f, None)

        getattr(self.store, f.__name__).add(data)
        return f

    def __getattribute__(self, name):

        if name != 'store' and name!='fmt' and (found := object.__getattribute__(object.__getattribute__(self, 'store'), name)):
            return found

        return object.__getattribute__(self, name)

    # def get_func_by_id(id: str):
