import sys
from functools import wraps
import datetime


def debug(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        ag = [item for item in args]
        kg = [item for item in kwargs]
        func_name = 'unknown'
        try:
            func_name = func.__qualname__
        except AttributeError:
            # python 2.7 doesn't have __qualname__
            pass
        sys.stderr.write(
            ">{func_name} with args:{ag}, kwargs:{kg} at {t}\n"
            .format(
                func_name=func_name,
                ag=ag, kg=kg,
                t=datetime.datetime.now()
            )
        )
        res = func(*args, **kwargs)
        sys.stderr.write(
            "\t-->{func_name}_result:{res} at {t}\n"
            .format(
                func_name=func_name,
                res=res,
                t=datetime.datetime.now()
            )
        )

        return res
    return wrap


def debug_with_prefix(prefix):
    """
    use @debug_with_prefix(">>>>") as decorator for python code
    it automatically prints out >>>func name and args
    """
    def debug(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            ag = [item for item in args]
            kg = [item for item in kwargs]
            func_name = 'unknown'
            try:
                func_name = func.__qualname__
            except AttributeError:
                # python 2.7 doesn't have __qualname__
                pass

            sys.stderr.write(
                "{prefix}{func_name} with args:{ag}, kwargs:{kg} at {t}\n"
                .format(
                    prefix=prefix,
                    func_name=func_name,
                    ag=ag, kg=kg,
                    t=datetime.datetime.now()
                )
            )
            res = func(*args, **kwargs)
            return res
        return wrap
    return debug


def debug_class(cls):
    """
    debug decorator for class
    """
    for key, val in vars(cls).items():
        if callable(val):
            setattr(cls, key, debug(val))
    return cls


class FuncCallCounter(type):
    """
    Meta class which decorates all the methods of the subclass using call_counter as the decorator
    example:
    #inherited as metaclass
    class A(metaclass=FuncCallCounter):
    def foo(self):
        pass
    def bar(self):
        pass
    """

    @staticmethod
    def call_counter(func):
        """
        decorator for counting calls of a function
        """
        def helper(*args, **kwargs):
            helper.calls += 1
            return func(*args, **kwargs)
        helper.calls = 0
        helper.__name__ = func.__name__

        return helper

    def __new__(cls, clsname, superclasses, attributedict):
        """
        Every method is decoratored with call_counter
        """
        for attr in attributedict:
            if callable(attributedict[attr]) and not attr.startswith("__"):
                attributedict[attr] = cls.call_counter(attributedict[attr])
        return type.__new__(cls, clsname, superclasses, attributedict)


def debug_with_ipdb_if_fail(func):
    """
    this wrapper will try to run the function if failed, import ipdb and then rerun itself
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        ag = [item for item in args]
        kg = [item for item in kwargs]
        func_name = 'unknown'
        try:
            func_name = func.__qualname__
        except AttributeError:
            # python 2.7 doesn't have __qualname__
            pass
        sys.stderr.write(
            ">{func_name} with args:{ag}, kwargs:{kg} at {t}\n"
            .format(
                func_name=func_name,
                ag=ag, kg=kg,
                t=datetime.datetime.now()
            )
        )
        try:
            res = func(*args, **kwargs)
        except:
            print('{} failed, importing ipdb'.format(func))
            import ipdb
            ipdb.set_trace()
            res = func(*args, **kwargs)
        sys.stderr.write(
            "\t-->{func_name}_result:{res} at {t}\n"
            .format(
                func_name=func_name,
                res=res,
                t=datetime.datetime.now()
            )
        )

        return res
    return wrap


