"""
Units class definitions for unit aware numbers and helpers.

Makes heavy uses of "unit strings" - abbreviated as "ustrings".  These strings
follow the formatting rules below,

1. units are abbreviated using standard SI base and derived units.
2. each component may include an exponent using the "^" symbol.
3. each unit^exponent set is separated by a dot (period) "."
4. parentheses may be used to group denominator sets

Some examples include...

    N  = kg.m.s^-2    = kg.m/s^2 = kg.m/(s^2)
    Pa = kg.m^-1.s^-2 = kg/m/s^2 = kg/(m.s^2)

Attempting to write pascals as "kg/m.s^2" is incorrect.

"""

import numpy as np

import re
import logging
import copy

from ..utilities import load_data_file
from ..exceptions import UnitsMissmatchException

logger = logging.getLogger(__name__)

def load_unit_context(context):
    """
    Loads a set of units from a json file.  the filename to be loaded is

    SI_units_<lower(context)>.json

    :param context: file identifier to load
    :return: dictionary mapping unit symbol to unit name, description, and base, where
        base is a representation of the unit in SI base types.
    """
    fname = f"SI_units_{context.lower()}"
    rdat = load_data_file(fname)
    subs = rdat.pop("_subs",dict())
    cdat = {s: {"n":d["name"], "info":d["quantity"], "u":Units.from_string(d["base"])} for s, d in rdat.items()}
    cdat["_subs"] = {k: (Units.from_string(k, context=context), Units.from_string(v, context=context)) for k, v in subs.items()}
    return cdat

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
            nvals = len(self.f)
        except TypeError:
            return self.s[0]
        
        if nvals < 5:
            return "["+", ".join([f"{v}" for v in self.f])+"]"
        else:
            return f"[{self.f[0]},... + {nvals-1} others]"

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

    def copy(self):
        return self.__copy__()

class Units(object):
    #re_den_group = re.compile(r"/\([a-zA-Z]+(?:\^[+-]?\d+)?(?:\.+[a-zA-Z]+(?:\^[+-]?\d+)?)*\)")
    re_den_group = re.compile(r"/\(([a-zA-Z]+(?:\^[+-]?\d+)?|1)?(?:\.+[a-zA-Z]+(?:\^[+-]?\d+)?)*\)")
    re_single_den = re.compile(r"/\.*(?P<u>[a-zA-Z]+)(?P<e>\^[+-]?\d+)?\.*")
    re_non_exp_sets = re.compile(r"(?:[a-zA-Z]+(?=\.))|(?:[a-zA-Z]+$)")

    CONTEXTS = dict()

    @classmethod
    def from_any(cls, other):
        if other is not None:
            if not isinstance(other, cls):
                try:
                    obj = cls.from_string(other)
                except (ValueError, TypeError):
                    logger.warning(f"units provided not an instance or a proper string... just using as is?: {other}")
                    obj = cls(other)
            else: # is a unit, just use it
                obj = other
        else: # return empty if none
            obj = cls()
        return obj

    @classmethod
    def from_string(cls, ustring, **kwargs):
        """
        Creates a Unit object from a string representation.

        :param ustring: units strng
        :return: new Units instance
        :raises TypeError: if input is not string type
        :raises ValueError: if ustring cannot be split cleanly
        """

        # set True to print each step to error log... regex is anoying..
        __DEBUG = False

        if ustring == "" or ustring == "1":
            return cls({}, **kwargs)

        # convert all /(u^e.u^e) to /u^e/u^e
        def splitd(s):
            d_subs = s.group(0).replace("(","").replace(")","").replace(".","/")
            return d_subs

        u_splitd = cls.re_den_group.sub(splitd, ustring)
        if __DEBUG: logger.error(f"u_splitd: {u_splitd}")

        # remove all /1 instances, remove all double //
        u_nosingles = u_splitd.replace("/1","").replace("//","/")
        if __DEBUG: logger.error(f"u_nosingles: {u_nosingles}")

        # flip all instances of "/u^e" to "u^-e"
        def flipe(s):
            e_neg = s.group("e")
            e = "-1" if e_neg is None else str(-int(e_neg[1:]))
            return "."+s.group("u")+"^"+e+"."

        u_flipped = cls.re_single_den.sub(flipe, u_nosingles)
        if __DEBUG: logger.error(f"u_flipped: {u_flipped}")

        # clean extra dots
        u_strip = re.sub(r"\.+", ".", u_flipped).strip(".")

        if __DEBUG: logger.error(f"u_strip: {u_strip}")

        # give all sets an exponent
        def addone(s):
            return s.group(0)+"^1"

        u_padded = cls.re_non_exp_sets.sub(addone, u_strip).strip(".")
        if __DEBUG: logger.error(f"u_padded: {u_padded}")


        # while splitting, remove all single '1' sets - caused by "1/..." sets
        u_parts = [ue.split("^") for ue in u_padded.split(".") if ue not in ('1', '(1)')]
        if __DEBUG: logger.error(f"u_parts: {u_parts}")

        s_full = dict()
        for ue0, ue1 in u_parts:
            s_full[ue0] = s_full.get(ue0,0) + int(ue1)
        logger.debug(f"Converter {ustring} in to {s_full}")

        s_full = {k: v for k, v in s_full.items() if v != 0}

        obj = cls(s_full, **kwargs)

        return obj

    def __init__(self, s=None, context="Electrical"):
        """
        Units class.  Should be called from one of the .from_* class methods
        in most cases.  If called directly, returns a unitless unit.

        Can be represented as a set of two arrays, each containing tuples
        of (str:unit, int:exponent).  Units are reconstructed as

            n[1][1]^n[1][2] ...
        u = --------------------
            d[1][1]^d[1][2] ...

        a string value of "1" is used to denote unit-less.  In such cases the
        exponent is ignored.

        Stored internally as one dict (s) using negative exponents.
        Unitless instances have s=={}
        """
        super().__init__()
        self.s = dict() if s is None else s
        self.context = context

    def __copy__(self):
        return copy.deepcopy(self)

    def __repr__(self):
        p1 = sorted([f"{s}^{e}" if e > 1 else s for s, e in self.s.items() if e > 0])
        p2 = sorted([f"{s}^{-e}" if e < -1 else s for s, e in self.s.items() if e < 0])
        return (".".join(p1) if len(p1) else "1")+(f"/({'.'.join(p2)})" if len(p2) else "")

    def __mul__(self, other):
        try: # get base data if exists
            s2 = other.s
        except AttributeError: # if not, try and make a new units from it
            s2 = self.__get_s_from_other(other)

        ur = {u: self.s.get(u,0) + s2.get(u,0) for u in set(self.s.keys() | s2.keys())}
        return Units(ur)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if self == other:
            return
        elif not len(self.s) and not isinstance(other, Units):
            return # we do not have units, and other is not a units class... no check
        else:
            raise UnitsMissmatchException(self, other, "subtraction")

    def __rsub__(self, other):
        if self == other:
            return
        elif not len(self.s) and not isinstance(other, Units):
            return # we do not have units, and other is not a units class... no check
        else:
            raise UnitsMissmatchException(other, self, "subtraction")

    def __add__(self, other):
        if self == other:
            return
        elif not len(self.s) and not isinstance(other, Units):
            return # we do not have units, and other is not a units class... no check
        else:
            raise UnitsMissmatchException(self, other, "addition")

    def __radd__(self, other):
        if self == other:
            return
        elif not len(self.s) and not isinstance(other, Units):
            return # we do not have units, and other is not a units class... no check
        else:
            raise UnitsMissmatchException(other, self, "addition")

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        # we are numerator, other is denominator
        try:  # get base data if exists
            s2 = other.s
        except AttributeError:  # if not, try and make a new units from it
            s2 = self.__get_s_from_other(other)

        ur = {u: self.s.get(u, 0) - s2.get(u, 0) for u in set(self.s.keys() | s2.keys())}
        return Units(ur)

    def __rtruediv__(self, other):
        # we are denominator, other is numerator
        try:  # get base data if exists
            s2 = other.s
        except AttributeError:  # if not, try and make a new units from it
            s2 = self.__get_s_from_other(other)

        ur = {u: s2.get(u, 0) - self.s.get(u, 0) for u in set(self.s.keys() | s2.keys())}
        return Units(ur)

    def __eq__(self, other):
        try:
            s2 = other.s
        except AttributeError:
            s2 = self.__get_s_from_other(other)
        return self.s == s2

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def __get_s_from_other(other):
        """
        Internal method. Attempts to get a units-exponents dictionary from an object.
        This should be called after an initial check for an "s" attribute is attempted.

        Used mainly as a helper for overloaded math functions.

        :return: a dictionary if possible.
        :raises InputError: if cannot convert a string to a units class
        :raises Exception: if something else happens, just passes it along.
        """
        try:
            ou = Units.from_string(other)
            s = ou.s
        except ValueError as e:
            logging.exception(f"Unable to convert input {other} to a unit for multiplication.")
            raise e
        except Exception as e:
            logging.exception(f"Unknown error during convert... {e}")
            raise e
        return s

    def as_base(self, context=None):
        """
        Expand the units to base units as much as possible.  Uses the instances context
        if none is give.  If a new context is specified, then updates this units default
        context to the new value, and loads the context if not already loaded
        :param context: new context as string, or None to use default
        :return: new units object with expanded units
        """
        if context is not None:
            self.context = context

        if self.context not in self.CONTEXTS.keys(): # load new context if we do not have it already
            Units.CONTEXTS[self.context] = load_unit_context(self.context)
            logger.info(f"Loaded new units context: {self.context}")

        cntxt = Units.CONTEXTS[self.context] # just to avoid typing a bunch...

        sbase = dict()
        for u, e in self.s.items():
            if u in cntxt.keys():
                for su, se in cntxt[u]["u"].s.items():
                    sbase[su] = sbase.get(su,0) + se*e
            else:
                sbase[u] = sbase.get(u, 0) + e
        
        return Units(s=sbase, context=self.context)

    def copy(self):
        return self.__copy__()

    def simplify(self, context=None):
        """
        Simplify the units as much as possible.  Uses the instances context
        if none is give.  If a new context is specified, then updates this units default
        context to the new value, and loads the context if not already loaded

        Only able to perform simplifications included in the context's simplification table, or
        into standard units.  Nothing complicated here... just lookups for common patterns.

        :param context: new context as string, or None to use default
        :return: new units object with simplified units
        """

        #TODO check if we are base units, and avoid warning about unable to simplify if so

        if context is not None:
            self.context = context

        if self.context not in self.CONTEXTS.keys():  # load new context if we do not have it already
            Units.CONTEXTS[self.context] = load_unit_context(self.context)

        # check basic units first
        for name, values in self.CONTEXTS[self.context].items():
            if name[0] == "_": # check first to avoid error
                pass
            elif values["u"] == self:
                return Units.from_string(name, context=self.context)
            else: # not found... go to next... do nothing :(
                pass

        # check subs next
        for key, value in self.CONTEXTS[self.context]["_subs"].items():
            if self == value[0]:
                return value[1].copy()
            else:
                pass

        # if we are here, we failed to simplify
        logger.warning(f"Unable to simplify {self} in context: {self.context}")

    @property
    def n(self):
        """
        Numerator sets
        :return: n = [(s, e), ...]
        """
        return Units({s: e for s, e in self.s.items() if e > 0})

    @property
    def d(self):
        """
        Denominator sets
        :return: d = [(s, e), ...]
        """
        return Units({s: -e for s, e in self.s.items() if e < 0})

