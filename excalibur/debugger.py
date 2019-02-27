import sys
from functools import wraps
def debug(func):
    @wraps(func)
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

def debug_with_prefix(prefix):
    def debug(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            ag = [item for item in args]
            kg = [item for item in kwargs]
            sys.stderr.write(
                "{prefix}{func_name} with args:{ag}, kwargs:{kg}\n"\
                .format(
                    prefix = prefix,
                    func_name = func.__qualname__,
                    ag = ag, kg = kg
                )
            )
            func(*args, **kwargs)
        return wrap
    return debug

