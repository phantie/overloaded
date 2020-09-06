from functools import wraps
from typeguard import typechecked
from operator import attrgetter
from functools import partial
from typing import get_type_hints, Union, Callable, Optional, Hashable, NamedTupleMeta, NamedTuple
from abc import abstractproperty, ABCMeta


__all__ = ['Overloader']

class NamedTupleABCMeta(ABCMeta, NamedTupleMeta): ...

class AbstractPacked(metaclass=NamedTupleABCMeta):
    @abstractproperty
    def sort_key(self): ...

    @abstractproperty
    def sort_reverse(self): ...

class Packed(NamedTuple, AbstractPacked):
    f: Callable
    hintcount: int
    original: Callable
    id: Hashable

    sort_key = attrgetter("hintcount")
    sort_reverse = True

class Aggregate:    
    _type = Packed

    def __init__(self):
        self._store = []

    def __call__(self, *args, **kwargs):
        idx = -1
        self._store.sort(reverse=self._type.sort_reverse, key = self._type.sort_key)  
        while True:
            idx += 1

            if idx >= len(self._store):
                if idx > 1:
                    error_msg = "functions exist, but with the different signatures"
                else:
                    error_msg = "function exists, but with a different signature"

                raise TypeError(error_msg)

            try:
                return self._store[idx].f(*args, **kwargs)

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

    def __init__(self, _type):
        self._type = _type

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self.__setattr__(name, self._type())
            return object.__getattribute__(self, name)

    def __getitem__(self, name):
        return self.__getattribute__(name)


class Overloader:

    def __init__(self):
        self.store = defaultnamespace(Aggregate)
    
    def __call__(self, var: Union[Callable, Optional[Hashable]]) -> Callable:
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