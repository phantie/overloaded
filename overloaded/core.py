from overloaded.hinting import strict_types
from operator import attrgetter
from functools import wraps

class IteratorOverListOfFunctions:

    def __init__(self):
        self._store = []

    def __call__(self, *args, **kwargs):
        idx = -1
        self._store.sort(reverse=True, key=attrgetter('hintcount'))
        while True:
            idx += 1

            try:
                result = self._store[idx](*args, **kwargs)
                return result

            except IndexError:
                if idx > 1:
                    error_msg = "Functions exist but with the different signatures."
                else:
                    error_msg = "Function exists but with a different signature."
                
                raise TypeError(error_msg)

            except (TypeError, NameError) as e:                
                if any(string in str(e) for string in ('Type of', 'missing', 'takes', 
                'not defined', 'unexpected', 'multiple')) and 'Type of result' not in str(e):
                    continue
                else:
                    raise e

    def __len__(self):
        return self._store.__len__()

    def append(self, f):
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

    def __init__(self):
        self.store = defaultnamespace(IteratorOverListOfFunctions)
    
    def __call__(self, f: callable):
        getattr(self.store, f.__name__).append(strict_types(f))
        return f

    def __getattribute__(self, name):

        if name != 'store' and (found := object.__getattribute__(object.__getattribute__(self, 'store'), name)):
            return found

        return object.__getattribute__(self, name)