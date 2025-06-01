
import logging
import copy

import numpy as np
from pyee.utilities import load_data_file
from pyee.types.aliases import t_numeric

type t_PrefixObj = Prefix

logger = logging.getLogger(__name__)

class Prefix(object):
    """
    SI prefixes.  Stored as three components...
    n = name   (i.e. kilo) (as list)
    f = factor (i.e. 1000) (as numpy array)
    s = symbol (i.e. k)    (as list)

    Call directly with a symbol, or use the helper class methods from_name or from_number

    Supports multiplication and division.  If used against another Prefix instance, returns a
    new Prefix instance.  Otherwise acts like a number and attempts the operation.
    """

    _DATA_FILE : str | None = None
    _data_by_symbol = dict()
    _data_by_name = dict()
    _data_by_value = dict()
    _data_value_scale = dict()

    __DEBUG = False

    @staticmethod
    def rebalance(num: float, prefix: t_PrefixObj | None = None) -> tuple[float, "Prefix"]:
        value = num*prefix.f if prefix is not None else num
        np = Prefix.from_number(value)
        nv = value/np.f
        return nv, np

    @classmethod
    def from_string(cls, pstring: str) -> t_PrefixObj:
        """
        Searches for a prefix matching the given symbol.  Does not check for multiple matches... as
        this should never happen.  
        
        If cannot find by name, tries by symbol.

        If no match is made, raises key error.

        Does not support array arguments.

        :param pstring: prefix string
        :return: prefix object if possible.
        """
        
        if cls._DATA_FILE is None: cls.reload_data()

        sym_data = cls._data_by_symbol.get(pstring, None)
        if sym_data is not None:
            return cls(pstring, sym_data['factor'], sym_data['name'])

        sym_data = cls._data_by_name.get(pstring, None)
        if sym_data is not None:
            return cls(sym_data['symbol'], sym_data['factor'], pstring)

        raise ValueError(f"Unknown symbol or name for new prefix: {pstring}, {cls._data_by_symbol}")

    @classmethod
    def from_number(cls, pnum: t_numeric) -> t_PrefixObj:
        """
        Returns the closest prefix to use for the given number.  Attempts to use a prefix that
        will result in a number formatted "well", meaning 1-3 digits ahead of the decimal place.

        :param pnum: number to find a prefix for
        :return: new prefix object
        """
        #TODO array-itize this... some messy lists mixed with arrays below.

        if cls._DATA_FILE is None: cls.reload_data()

        # if greater than 1, we want the next smallest factor.
        #scalar was: diffs = [1 if (pnum - v) >= 0 else 0 for v in cls._data_value_scale]
        diffs = np.array([1*((pnum - v) >= 0) for v in cls._data_value_scale])
        if cls.__DEBUG: logger.error(f"... ... PREFIX: diffs={diffs}")


        factor = cls._data_value_scale[max(np.max(diffs.nonzero()),0)] #type: ignore , will fail if diffs has too many elements
        symbol = cls._data_by_value[factor]["symbol"]
        name = cls._data_by_value[factor]["name"]
        return cls(symbol, factor, name)

    @classmethod
    def reload_data(cls, datafile : str = "SI_prefixes") -> None:
        cls._DATA_FILE = datafile
        cls._data_by_symbol = load_data_file(cls._DATA_FILE)
        cls._data_by_value = {d["factor"]: {"symbol":s, "name":d["name"]} for s, d in cls._data_by_symbol.items()}
        cls._data_value_scale = sorted(cls._data_by_value.keys())
        cls._data_by_name = {d["name"]: {"symbol":s, "factor":d["factor"]} for s, d in cls._data_by_symbol.items()}

    def __new__(cls, *args, **kwargs) -> t_PrefixObj:
        # make sure we have loaded dicts before making an object
        if cls._DATA_FILE is None: 
            cls.reload_data()
        return super().__new__(cls)

    def __init__(self, symbol: str, factor: t_numeric, name : str) -> None:
        self.f = factor
        self.n = name
        self.s = symbol

    def __copy__(self):
        return copy.deepcopy(self)

    def __repr__(self):
        if self.n == "":
            return f"Prefix [Nameless]: {self.f}"
        else:
            return f"Prefix [{self.s}] {self.n}: {self.f}"

    def __str__(self):
        try: # On success, array, on fial, single value
            nvals = len(self.s)
        except TypeError:
            return self.s
        
        if nvals < 5:
            return "["+", ".join([f"{v}" for v in self.s])+"]"
        else:
            return f"[{self.s[0]},... + {nvals-1} others]"

    def __mul__(self, other) -> "t_PrefixObj | t_numeric":
        if isinstance(other, Prefix):
            return Prefix.from_number(self.f * other.f)
        else:
            return self.f * other

    def __rmul__(self, other) -> "t_PrefixObj | t_numeric":
        if isinstance(other, Prefix):
            return Prefix.from_number(other.f * self.f)
        else:
            return other * self.f

    def __div__(self, other) -> "t_PrefixObj | t_numeric":
        return self.__truediv__(other)

    def __rdiv__(self, other) -> "t_PrefixObj | t_numeric":
        return self.__rtruediv__(other)

    def __truediv__(self, other) -> "t_PrefixObj | t_numeric":
        if isinstance(other, Prefix):
            return Prefix.from_number(self.f / other.f)
        else:
            return self.f / other

    def __rtruediv__(self, other) -> "t_PrefixObj | t_numeric":
        if isinstance(other, Prefix):
            return Prefix.from_number(other.f / self.f)
        
        if self.__DEBUG: logger.error(f"rdiv for {self} and {other}")

        return other / self.f

    def __eq__(self, other) -> bool:
        try:  # if both have a factor, return that equality
            return self.f == other.f
        except AttributeError:
            pass

        try: # if other can be a float, try that...
            return self.f == float(other)
        except ValueError:
            pass

        return self.s == other # default to checking by symbol...

    def __neq__(self, other) -> bool:
        return not self.__eq__(other)

    def copy(self) -> t_PrefixObj:
        return self.__copy__()
