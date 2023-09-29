import asyncio
import inspect
from typing import Callable, Type, Optional

_wrapper_self_of_cls = None


class Wrapper:
    # noinspection PyMethodParameters
    def __new__(_cls, *args, **kwargs):

        def _wrapper(self_of_cls=None, *a, **kw):
            global _wrapper_self_of_cls
            if not isinstance(self_of_cls, object):
                if not issubclass(self_of_cls, type):
                    _wrapper_self_of_cls = True
                else:
                    _wrapper_self_of_cls = self_of_cls
            else:
                _wrapper_self_of_cls = self_of_cls
            wrapper = _cls(*args, **kwargs)
            return wrapper(*a, **kw)

        global _wrapper_self_of_cls
        if _wrapper_self_of_cls is None:
            return _wrapper

        __init__ = _cls.__init__

        def __wrapper_init__(self, *a, **kw):
            global _wrapper_self_of_cls
            if _wrapper_self_of_cls is None:
                return  # Do nothing
            kw["_wrapper_self_of_cls"] = _wrapper_self_of_cls
            _wrapper_self_of_cls = None
            __init__(self, *a, **kw)

        __wrapper_init__.__wrapped_init__ = True

        if not getattr(__init__, "__wrapped_init__", False):
            _cls.__init__ = __wrapper_init__

        return super().__new__(_cls)

    def __init__(self, cls, method, hook=None, _wrapper_self_of_cls=None, **kwargs):
        self._cls = cls
        self._is_cls = True
        self._method = method
        self._hook = hook
        self._hook_disabled = False
        self._wrapper_self_of_cls = _wrapper_self_of_cls
        self._is_self = True
        self._kwargs = kwargs
        self._method_signature = inspect.signature(self.method)

        # check if cls in signature
        if "cls" not in self.method_signature.parameters.keys():
            self._is_cls = False
        # check if self in signature
        if "self" not in self.method_signature.parameters.keys():
            self._is_self = False

    def __str__(self):
        if self.cls is not None:
            return f"{self.cls.__name__}.{self.method.__name__} -> {self.kwargs}"
        return f"{self.method.__name__} -> {self.kwargs}"

    def __getattr__(self, item):
        if item.startswith("_"):
            return super().__getattribute__(item)
        if item in ["self", "cls", "method", "hook", "kwargs"]:
            return super().__getattribute__(item)
        return self._kwargs[item]

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)
        if key in ["self", "cls", "method", "hook", "kwargs"]:
            return super().__setattr__(key, value)
        self._kwargs[key] = value

    def __getitem__(self, item):
        return self._kwargs[item]

    def __setitem__(self, key, value):
        self._kwargs[key] = value

    def __iter__(self):
        return iter(self._kwargs)

    def __call__(self, *args, **kwargs):
        is_hook_async = inspect.iscoroutinefunction(self.hook)
        is_method_async = inspect.iscoroutinefunction(self.method)

        if self.self is not None:
            if self.hook is not None and not self.hook_disabled:
                self._hook_disabled = True
                if not is_hook_async:
                    return self.hook(self, *args, **kwargs)
                return asyncio.get_running_loop().create_task(self.hook(self, *args, **kwargs))
            if not is_method_async:
                return self.method(self.self, *args, **kwargs)
            return asyncio.get_running_loop().create_task(self.method(self.self, *args, **kwargs))
        if self.cls is not None:
            if not is_method_async:
                return self.method(self.cls, *args, **kwargs)
            return asyncio.get_running_loop().create_task(self.method(self.cls, *args, **kwargs))
        if not is_method_async:
            return self.method(*args, **kwargs)
        return asyncio.get_running_loop().create_task(self.method(*args, **kwargs))

    @property
    def self(self):
        if not self._is_self:
            return None
        if isinstance(self._wrapper_self_of_cls, object):
            return self._wrapper_self_of_cls
        return None

    @self.setter
    def self(self, value):
        self._wrapper_self_of_cls = value

    @property
    def cls(self) -> Optional[Type]:
        if not self._is_cls:
            return None
        return self._cls

    @cls.setter
    def cls(self, value):
        self._cls = value

    @property
    def method(self) -> Callable:
        return self._method

    @property
    def method_signature(self) -> inspect.Signature:
        return self._method_signature

    @property
    def hook(self) -> Callable:
        return self._hook

    @property
    def hook_disabled(self) -> bool:
        return self._hook_disabled

    @property
    def kwargs(self):
        return self._kwargs
