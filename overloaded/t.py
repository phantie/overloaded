class A:
    a = 1
    b = 2

def collect(cls):
    for item in vars(cls).items():
        print(item)
        if isinstance(item, FunctionType) and getattr(item, "marked", False):
            cls.marked_funcs.append(item)
    return cls

collect(A)