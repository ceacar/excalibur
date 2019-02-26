def memoize(time_to_expire = 3600*5):
    def memoize_things(function):
        def inner(*args, **kwargs):
            key1 = tuple(args)
            key2 = tuple(kwargs)
            val = cache_get((key1,key2))
            if val:
                return val 
            new_val = function(*args,**kwargs)
            cache_set((key1, key2), new_val, expire_time = time_to_expire)
            return new_val

        return inner
    return memoize_things

