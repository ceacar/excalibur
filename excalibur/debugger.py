import sys
def debug(func):
    def wrap(*args, **kwargs):
        ag = [item for item in args]
        kg = [item for item in kwargs]
        sys.stderr.write(
            ">{func_name} with args:{ag}, kwargs:{kg}\n"\
            .format(
                func_name = func.__qualname__,
                ag = ag, kg = kg
            )
        )
        func(*args, **kwargs)
    return wrap
