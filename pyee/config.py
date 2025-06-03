"""
Configuration module.
"""
from abc import ABCMeta, abstractmethod
from types import UnionType
from typing import Any

class ConfigParameter(object, metaclass=ABCMeta):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
          cls.instance = super(ConfigParameter, cls).__new__(cls)
        return cls.instance

    def __init__(self, default: Any) -> None:
        self.parameter = default

    def get(self):
        return self.parameter
    
    def set(self, value):
        self.parameter = value

    def __bool__(self):
        return bool(self.parameter)

    def __eq__(self, other: Any) -> bool:
        return self.parameter == other

    def __ne__(self, other: Any) -> bool:
        return self.parameter != other


class BooleanConfigParameter(ConfigParameter):
    def __init__(self, default: bool=False) -> None:
        self.parameter = bool(default)

    def set(self, value):
        self.parameter = bool(value)
    
    def __or__(self, other: Any) -> bool:
        return self.parameter or other

    def __ror__(self, other: Any) -> bool:
        return other or self.parameter
    
    def __and__(self, other: Any) -> bool:
        return self.parameter and other

    def __rand__(self, other: Any) -> bool:
        return other and self.parameter


class NumericConfigParameter(ConfigParameter):
    def __init__(self, default: float=1.0) -> None:
        self.parameter = float(default)

    def __mul__(self, other):
        return self.parameter * other

    def __rmul__(self, other):
        return other * self.parameter

    def __truediv__(self, other):
        return self.parameter / other

    def __rtruediv__(self, other):
        return other / self.parameter

    def __div__(self, other):
        return self.parameter / other

    def __rdiv__(self, other):
        return other / self.parameter

    def __sub__(self, other):
        return self.parameter - other

    def __rsub__(self, other):
        return other - self.parameter

    def __add__(self, other):
        return self.parameter + other

    def __radd__(self, other):
        return other + self.parameter
    
    def __gt__(self, other):
        return self.parameter > other

    def __gte__(self, other):
        return self.parameter >= other

    def __lt__(self, other):
        return self.parameter < other

    def __lte__(self, other):
        return self.parameter <= other


class OptionsConfigParameter(ConfigParameter):
    def __init__(self, default: str, options: list | tuple | set= set()) -> None:
        self.parameter = default
        self.options = options

        if not len(self.options):
            self.options = {default}

    def set(self, value: Any) -> None:
        if value not in self.options:
            raise ValueError(f"Unknown parameter value give: {value}.  Options are {self.options}.")
        self.parameter = value