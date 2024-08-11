import json
import functools
import copy
class CacheMethod:
    def __init__(self, func):
        self.func = func
        self._cache = {}
        functools.update_wrapper(self, func)
    
    def __call__(self, class_instance, *args, **kwargs):
        key = json.dumps((args,kwargs))
        if key not in self._cache.keys():
            self._cache[key] = self.func(class_instance, *args, **kwargs)
        return copy.deepcopy(self._cache[key])
    
    def __get__(self, instance, owner):
        """
        Fix: make our decorator class a decorator, so that it also works to
        decorate instance methods.
        https://stackoverflow.com/a/30105234/10237506
        """
        from functools import partial
        return partial(self.__call__, instance)