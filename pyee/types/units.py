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

import re
import logging
import copy

from typing import Callable

from pyee.regex import re_ustring_den_group, re_ustring_non_exp_sets, re_ustring_single_den
from pyee.utilities import load_data_file
from pyee.exceptions import UnitsMissmatchException, UnitsConversionException, UnitsConstructionException

type t_UnitObj = Units
type t_UnitsSource = str | dict | t_UnitObj | None

logger = logging.getLogger(__name__)

def load_unit_context(context: str) -> dict:
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
    cdat = {s: {"n":d["name"], "info":d["quantity"], "u":Units.from_string(d["base"]), 
                "c": d.get("conversions", dict())} for s, d in rdat.items()}
    cdat["_subs"] = {k: (Units.from_string(k, context=context), Units.from_string(v, context=context)) for k, v in subs.items()}
    return cdat

class Units(object):
    CONTEXTS = dict()

    @classmethod
    def create_unitless(cls, **kwargs) -> t_UnitObj:
        """
        Returns a unitless class object
        """
        return cls(dict(), **kwargs)

    @classmethod
    def from_any(cls, other : t_UnitsSource) -> t_UnitObj:
        """
        Create a new Units class from either a string or an existing units instance.
        """

        if isinstance(other, cls): # new unit from existing unit... just return it.
            return other
        elif other is None: # return empty unit (unitless)
            return cls.create_unitless()

        try: # maybe string like enough?
            return cls.from_string(other) #type: ignore
        except (ValueError, TypeError):
            pass        

        try: # dictionary like?
            len(other) #type: ignore
            other.keys() #type: ignore
            other.items() #type: ignore
            return cls(other) #type: ignore
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Unable to make new unit from {other}")
            raise TypeError(f"Unable to make new unit from {other}.  Original exception was {e}")

    @classmethod
    def from_string(cls, ustring : str, **kwargs) -> t_UnitObj:
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
            return cls.create_unitless(**kwargs)

        # convert all /(u^e.u^e) to /u^e/u^e
        def splitd(s):
            d_subs = s.group(0).replace("(","").replace(")","").replace(".","/")
            return d_subs

        u_splitd = re_ustring_den_group.sub(splitd, ustring)
        if __DEBUG: logger.error(f"u_splitd: {u_splitd}")

        # remove all /1 instances, remove all double //
        u_nosingles = u_splitd.replace("/1","").replace("//","/")
        if __DEBUG: logger.error(f"u_nosingles: {u_nosingles}")

        # flip all instances of "/u^e" to "u^-e"
        def flipe(s):
            e_neg = s.group("e")
            e = "-1" if e_neg is None else str(-int(e_neg[1:]))
            return "."+s.group("u")+"^"+e+"."
        u_flipped = re_ustring_single_den.sub(flipe, u_nosingles)
        if __DEBUG: logger.error(f"u_flipped: {u_flipped}")

        # remove all parentheses - not needed anymore hopefully?
        u_together = re.sub(r"[()]", "", u_flipped).strip(".")

        # clean extra dots
        u_strip = re.sub(r"\.+", ".", u_flipped).strip(".")

        if __DEBUG: logger.error(f"u_strip: {u_strip}")

        # give all sets an exponent
        def addone(s):
            return s.group(0)+"^1"

        u_padded = re_ustring_non_exp_sets.sub(addone, u_strip).strip(".")
        if __DEBUG: logger.error(f"u_padded: {u_padded}")


        # while splitting, remove all single '1' sets - caused by "1/..." sets
        u_parts = [ue.split("^") for ue in u_padded.split(".") if ue not in ('1', '(1)')]
        if __DEBUG: logger.error(f"u_parts: {u_parts}")


        s_full = dict()
        try:
            for ue0, ue1 in u_parts:
                s_full[ue0] = s_full.get(ue0,0) + int(ue1)
        except ValueError: # sometimes failes if an element of u_parts did not split into 2
            logger.debug(f"Failed converting {ustring} in to {s_full}")
            raise UnitsConstructionException(ustring, (u_strip, u_padded, u_parts, s_full))
            


        logger.debug(f"Converter {ustring} in to {s_full}")

        s_full = {k: v for k, v in s_full.items() if v != 0}

        obj = cls(s_full, **kwargs)

        return obj

    def __init__(self, s : dict, context : str = "Electrical") -> None:
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
        self.s = s
        self.context = context

    def __copy__(self):
        return Units(s=self.s.copy())

    def __repr__(self):
        p1 = sorted([f"{s}^{e}" if e > 1 else s for s, e in self.s.items() if e > 0])
        p2 = sorted([f"{s}^{-e}" if e < -1 else s for s, e in self.s.items() if e < 0])
        return (".".join(p1) if len(p1) else "1")+(f"/({'.'.join(p2)})" if len(p2) else "")

    def __mul__(self, other):
        try: # get base data if exists
            s2 = other.s
        except AttributeError: # if not, try and make a new units from it
            u2 = self.from_any(other)
            s2 = u2.s
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
            u2 = self.from_any(other)
            s2 = u2.s

        ur = {u: self.s.get(u, 0) - s2.get(u, 0) for u in set(self.s.keys() | s2.keys())}
        return Units(ur)

    def __rtruediv__(self, other):
        # we are denominator, other is numerator
        if other == 1: # simple case... we are just inverting units...
            udict_flipped = {k: -v for k, v in self.s.items()}
            return Units(udict_flipped)

        try:  # get base data if exists
            s2 = other.s
        except AttributeError:  # if not, try and make a new units from it
            u2 = self.from_any(other)
            s2 = u2.s

        ur = {u: s2.get(u, 0) - self.s.get(u, 0) for u in set(self.s.keys() | s2.keys())}
        return Units(ur)

    def __eq__(self, other):
        try:
            s2 = other.s
        except AttributeError:
            u2 = self.from_any(other)
            s2 = u2.s
        
        return self.s == s2

    def __ne__(self, other):
        return not self.__eq__(other)

    def convert_to(self, newunits: t_UnitObj) -> Callable:
        """
        Tries to allow unit conversion.  Only really works on base units for now.
        Returns a function that can be called on numbers to convert to the new units.
        """

        if self == newunits: # take care of easy case first...
            return lambda x: x

        if self.context not in self.CONTEXTS.keys(): # load new context if we do not have it already
            Units.CONTEXTS[self.context] = load_unit_context(self.context)
            logger.info(f"Loaded new units context: {self.context}")

        selfinfo = self.CONTEXTS[self.context].get(str(self), None)
        if selfinfo is None:
            raise UnitsConversionException(self, newunits, 
                                           notes="Initial units do not exist in context - not a basic unit?")
        convfactors = selfinfo.get("c", dict()).get(str(newunits), None)
        if convfactors is None:
            raise UnitsConversionException(self, newunits, 
                                           notes=f"Cant find a conversion factor... self info is {selfinfo}")            

        return lambda x: convfactors[0] + convfactors[1]*x

    def as_base(self, context : str | None = None) -> t_UnitObj:
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

    def copy(self) -> "Units":
        return self.__copy__()

    def simplify(self, context : str | None = None) -> t_UnitObj:
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
        return self

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

    @property
    def unitless(self):
        return len(self.s) == 0