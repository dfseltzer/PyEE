"""
Main class definitions for unit aware numbers and helpers.

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

import re
import logging

from ..utilities import load_data_file

logger = logging.getLogger(__name__)

class PhysicalQuantity:
    def __init__(self, value=None, units=None, prefix=None):
        self.v = value
        self.p = prefix
        if not isinstance(units, Units):
            try:
                units = Units.from_string(units)
            except (ValueError, TypeError):
                logger.debug(f"units provided not an instance or a proper string... just using as is: {units}")
                units = Units(units)
        self.u = units


class Prefix:
    """
    SI prefixes.  Stored as three components...
    n = name   (i.e. kilo)
    f = factor (i.e. 1000)
    s = symbol (i.e. k)

    Call directly with a symbol, or use the helper class methods from_name or from_number
    """
    _DATA_FILE = "SI_prefixes"
    _data_by_symbol = None
    _data_by_name = None
    _data_by_value = None
    _data_value_scale = None

    @classmethod
    def from_name(cls, pstring):
        """
        Searches for a prefix matching the given symbol.  Does not check for multiple matches... as
        this should never happen.  If no match is made, raises key error.
        :param pstring:
        :return:
        """
        pobj = Prefix() # forces load of initial dict... dumb but simple

        if cls._data_by_name is None:
            cls._data_by_name = {d["name"]: {"symbol":s, "factor":d["factor"]} for s, d in cls._data_by_symbol.items()}

        pdata = cls._data_by_name[pstring]

        pobj.n = pstring
        pobj.f = pdata["factor"]
        pobj.s = pdata["symbol"]

        return pobj


    @classmethod
    def from_number(cls, pnum):
        """
        Returns the closest prefix to use for the given number.  Attempts to use a prefix that
        will result in a number formatted "well", meaning 1-3 digits ahead of the decimal place.

        :param pnum: number to find a prefix for
        :return: new prefix object
        """
        pobj = Prefix()  # forces load of initial dict... dumb but simple
        if cls._data_by_value is None:
            cls._data_by_value = {d["factor"]: {"symbol":s, "name":d["name"]} for s, d in cls._data_by_symbol.items()}
            cls._data_value_scale = sorted(cls._data_by_value.keys())

        # if greater than 1, we want the next smallest factor.
        diffs = [1 if (pnum - v) > 0 else 0 for v in cls._data_value_scale]

        factornum = cls._data_value_scale[max(diffs.index(0)-1,0)]

        pobj.s = cls._data_by_value[factornum]["symbol"]
        pobj.n = cls._data_by_value[factornum]["name"]
        pobj.f = factornum

        return pobj

    def __init__(self, symbol=None):
        if self._data_by_symbol is None:
            Prefix._data_by_symbol = load_data_file(Prefix._DATA_FILE)

        self.f = None
        self.n = None
        self.s = symbol

        if self.s is None:
            return

        self.f = self._data_by_symbol[symbol]["factor"]
        self.n = self._data_by_symbol[symbol]["name"]


class Units:
    re_den_group = re.compile(r"/\([a-zA-Z]+(?:\^[+-]?\d+)?(?:\.+[a-zA-Z]+(?:\^[+-]?\d+)?)*\)")
    re_single_den = re.compile(r"/(?P<u>[a-zA-Z]+)(?P<e>\^[+-]?\d+)?")
    re_non_exp_sets = re.compile(r"(?:[a-zA-Z]+(?=\.))|(?:[a-zA-Z]+$)")

    @classmethod
    def from_string(cls, ustring):
        """
        Creates a Unit object from a string representation.

        :param ustring:
        :return: new Units instance
        :raises TypeError: if input is not string type
        :raises ValueError: if ustring cannot be split cleanly
        """

        #logger.debug(f"Converting {ustring}")
        # convert all /(u^e.u^e) to /u^e/u^e
        def splitd(s):
            d_subs = s.group(0).replace("(","").replace(")","").replace(".","/")
            return d_subs

        u_splitd = cls.re_den_group.sub(splitd, ustring)
        #logger.debug(f"Step1:     {u_splitd}")

        # flip all instances of "/u^e" to "u^-e"
        def flipe(s):
            e_neg = s.group("e")
            e = "-1" if e_neg is None else str(-int(e_neg[1:]))
            return "."+s.group("u")+"^"+e+"."

        u_flipped = cls.re_single_den.sub(flipe, u_splitd)
        #logger.debug(f"Step2:     {u_flipped}")

        # clean extra dots
        u_strip = re.sub(r"\.+", ".", u_flipped)
        #logger.debug(f"Step3:     {u_strip}")

        # give all sets an exponent
        def addone(s):
            return s.group(0)+"^1"

        u_padded = cls.re_non_exp_sets.sub(addone, u_strip).strip(".")
        #logger.debug(f"Step4:     {u_padded}")

        u_parts = [ue.split("^") for ue in u_padded.split(".")]
        s_full = dict()
        for ue0, ue1 in u_parts:
            s_full[ue0] = s_full.get(ue0,0) + int(ue1)
        logger.debug(f"Converter {ustring} in to {s_full}")

        s_full = {k: v for k, v in s_full.items() if v != 0}

        obj = cls(s_full)

        return obj

    def __init__(self, s=None):
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

        Stored internally as one dict (s) using negative exponents
        """
        self.s = {"1":1} if s is None else s

    def __repr__(self):
        p1 = sorted([f"{s}^{e}" if e > 1 else s for s, e in self.s.items() if e > 0])
        p2 = sorted([f"{s}^{-e}" if e < -1 else s for s, e in self.s.items() if e < 0])
        return (".".join(p1) if len(p1) else "1")+(f"/({".".join(p2)})" if len(p2) else "")

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
        raise TypeError(f"Units do not support subtraction (not equal) for {self} and {other}")

    def __rsub__(self, other):
        if self == other:
            return
        raise TypeError(f"Units do not support (r)subtraction (not equal) for {self} and {other}")

    def __add__(self, other):
        if self == other:
            return
        raise TypeError(f"Units do not support addition (not equal) for {self} and {other}")

    def __radd__(self, other):
        if self == other:
            return
        raise TypeError(f"Units do not support (r)addition (not equal) for {self} and {other}")

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

    def __get_s_from_other(self, other):
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
        except InputError as e:
            logging.exception(f"Unable to convert input {other} to a unit for multiplication.")
            raise e
        except Exception as e:
            logging.exception(f"Unknown error during convert... {e}")
            raise e
        return s

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