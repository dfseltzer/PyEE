
import logging
import copy

import numpy as np

from ..utilities import load_data_file

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

    _DATA_FILE = "SI_prefixes"
    _data_by_symbol = None
    _data_by_name = None
    _data_by_value = None
    _data_value_scale = None

    __DEBUG = False

    @staticmethod
    def from_name(pstring):
        """
        Searches for a prefix matching the given symbol.  Does not check for multiple matches... as
        this should never happen.  If no match is made, raises key error.

        Does not support array arguments.

        :param pstring: prefix string
        :return: prefix object if possible.
        """
        pobj = Prefix() # forces load of initial dict... dumb but simple

        pdata = Prefix._data_by_name[pstring] # type: ignore

        pobj.n = pstring
        pobj.f = pdata["factor"]
        pobj.s = pdata["symbol"]

        return pobj

    @staticmethod
    def from_number(num):
        """
        Returns the closest prefix to use for the given number.  Attempts to use a prefix that
        will result in a number formatted "well", meaning 1-3 digits ahead of the decimal place.

        :param pnum: number to find a prefix for
        :return: new prefix object
        """
        #TODO array-itize this... some messy lists mixed with arrays below.

        pobj = Prefix()  # forces load of initial dict... dumb but simple

        pnum = abs(num)

        # if greater than 1, we want the next smallest factor.
        #scalar was: diffs = [1 if (pnum - v) >= 0 else 0 for v in cls._data_value_scale]
        diffs = np.array([1*((pnum - v) >= 0) for v in Prefix._data_value_scale]) # type: ignore
        pobj.f = Prefix._data_value_scale[max(np.max(diffs.nonzero()),0)] # type: ignore
        pobj.s = Prefix._data_by_value[pobj.f]["symbol"] # type: ignore
        pobj.n = Prefix._data_by_value[pobj.f]["name"] # type: ignore
        return pobj

    def __init__(self, symbol=""):
        if Prefix._data_by_symbol is None:
            Prefix._data_by_symbol = load_data_file(Prefix._DATA_FILE)
            Prefix._data_by_value = {d["factor"]: {"symbol":s, "name":d["name"]} for s, d in Prefix._data_by_symbol.items()}
            Prefix._data_value_scale = sorted(Prefix._data_by_value.keys())
            Prefix._data_by_name = {d["name"]: {"symbol":s, "factor":d["factor"]} for s, d in Prefix._data_by_symbol.items()}

        self.f = 1
        self.n = ""
        self.s = symbol

        if self.s is None:
            return

        self.f = self._data_by_symbol[symbol]["factor"]  # type: ignore
        self.n = self._data_by_symbol[symbol]["name"]  # type: ignore

    def __copy__(self):
        return copy.deepcopy(self)

    def __repr__(self):
        if self.n == "":
            return f"Prefix [Nameless]: {self.f}"
        else:
            return f"Prefix [{self.s}] {self.n}: {self.f}"

    def __str__(self):
        try:
            nvals = len(self.f) # type: ignore
        except TypeError:
            return self.s[0]
        
        if nvals < 5:
            return "["+", ".join([f"{v}" for v in self.f])+"]"  # type: ignore
        else:
            return f"[{self.f[0]},... + {nvals-1} others]"  # type: ignore

    def __mul__(self, other):
        if isinstance(other, Prefix):
            return Prefix.from_number(self.f * other.f)
        else:
            return self.f * other

    def __rmul__(self, other):
        if isinstance(other, Prefix):
            return Prefix.from_number(other.f * self.f)
        else:
            return other * self.f

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        if isinstance(other, Prefix):
            return Prefix.from_number(self.f / other.f)
        else:
            return self.f / other

    def __rtruediv__(self, other):
        if isinstance(other, Prefix):
            return Prefix.from_number(other.f / self.f)
        
        if self.__DEBUG: logger.error(f"rdiv for {self} and {other}")

        return other / self.f

    def __eq__(self, other):
        try:  # if both have a factor, return that equality
            return self.f == other.f
        except AttributeError:
            pass

        try: # if other can be a float, try that...
            return self.f == float(other)
        except ValueError:
            pass

        return self.s == other # default to checking by symbol...

    def __neq__(self, other):
        return not self.__eq__(other)

    def copy(self):
        return self.__copy__()
