from operator import attrgetter
from functools import wraps
from typeguard import typechecked
from typing import get_type_hints
from collections import namedtuple
from copy import deepcopy
from operator import itemgetter
from functools import partial
from typing import Union, Callable, Optional, Hashable

__all__ = ['Overloader']

class Aggregate:

    _type = namedtuple('_type', ['f', 'hintcount', 'original', 'id'])

    def __init__(self):
        self._store = []

    def __call__(self, *args, **kwargs):
        idx = -1
        self._store.sort(reverse=True, key = itemgetter(1))  
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

    def add(self, *args, **kwargs):
        self._store.append(self._type(*args, **kwargs))

    def with_id(self, id) -> Callable:
        """The main purpose for this feature is to ease the burden of debugging, 
        considering in the mean time calling the function with, for eg. overloaded.foo(),
        catches all the the TypeErrors, but the one it raises itself, 
        if none of the stored functions can be called with given arguments.

        Returns the original function.
        """

        assert id is not None

        for el in self._store:
            if el.id == id:
                return el.original
        else:
            raise KeyError(f'Function with id {id} does not exists.')
        

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

    def __init__(self):
        self.store = defaultnamespace(Aggregate)
    
    def __call__(self, var: Union[Callable, Optional[Hashable]]) -> Callable:
        def process(f, id=None):
            def get_type_hint_count(f):
                return len(get_type_hints(f))

            hintcount = get_type_hint_count(f)
            typechecked_f = typechecked(f, always=True)

            self.store.__getattribute__(f.__name__).add(typechecked_f, hintcount, f, id)
            return f

        if callable(var):
            return process(var)
        else:
            return partial(process, id=var)


    def __getattribute__(self, name):

        if name != 'store' and (found := object.__getattribute__(object.__getattribute__(self, 'store'), name)):
            return found

        return object.__getattribute__(self, name)
