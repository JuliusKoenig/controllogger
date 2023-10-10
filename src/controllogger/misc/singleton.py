from abc import ABCMeta
from typing import Any, Union


class Singleton(ABCMeta):
    """
    Singleton metaclass
    """

    singleton_map: dict[str, Any] = {}

    def __new__(cls, name, bases, attrs):
        __init__ = attrs.pop("__init__", None)

        def singleton__init__(self, *args, **kwargs):
            self_name = self.__class__.__name__
            if self_name not in Singleton.singleton_map:
                Singleton.singleton_map[self_name] = self
                if __init__ is not None:
                    __init__(self, *args, **kwargs)
            else:
                raise RuntimeError(f"Singleton {self_name} already initialized. Use {self_name}() to get the instance.")

        attrs["__singleton__"] = True

        # check if __singleton__ is set on bases
        singleton_set = False
        for base in bases:
            if hasattr(base, "__singleton__"):
                singleton_set = True
                break

        if not singleton_set:
            attrs["__init__"] = singleton__init__

        # check if BaseModel in bases
        base_model_set = False
        for base in bases:
            if base.__name__ == "BaseModel":
                base_model_set = True
                break

        if not base_model_set:
            return ABCMeta.__new__(cls, name, bases, attrs)
        else:
            return super().__new__(cls, name, bases, attrs)

    def __call__(cls, *args, init: bool = True, **kwargs):
        if init:
            if cls.__name__ not in Singleton.singleton_map:
                return super().__call__(*args, **kwargs)
            else:
                return cls.get_by_name(cls.__name__)
        else:
            if cls.__name__ in Singleton.singleton_map:
                return cls.get_by_name(cls.__name__)
            else:
                raise RuntimeError(f"Singleton {cls.__name__} not initialized. Call {cls.__name__}() first.")

    @classmethod
    def get_all(cls) -> dict[str, Any]:
        return cls.singleton_map

    @classmethod
    def get_by_name(cls, name: str) -> Any:
        current = cls.get_all().get(name, None)
        if current is None:
            raise RuntimeError(f"Singleton {name} not found.")
        return current

    @classmethod
    def get_by_type(cls, t: Union[type, str]) -> Any:
        if isinstance(t, str):
            searching_name = t
        elif isinstance(t, type):
            searching_name = t.__name__
        else:
            raise TypeError(f"Type of 't' must be 'str' or 'type', not '{type(t)}'.")
        for _, instance in cls.get_all().items():
            if isinstance(t, str):
                if instance.__class__.__name__ == searching_name:
                    return instance

                # get all bases
                bases = instance.__class__.__bases__
                for base in bases:
                    if base.__name__ == searching_name:
                        return instance
            elif isinstance(t, type):
                if isinstance(instance, t):
                    return instance
        raise RuntimeError(f"Singleton {searching_name} not found.")
