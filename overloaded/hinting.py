from typing import get_type_hints

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
