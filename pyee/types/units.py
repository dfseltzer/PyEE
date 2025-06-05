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

from typing import Callable
from functools import singledispatchmethod

from pyee.config import OptionsConfigParameter # import so we can register for single dispatch... do we need to?
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
    __DEBUG=False

    @classmethod
    def create_unitless(cls, **kwargs) -> t_UnitObj:
        """
        Returns a unitless class object
        """
        return cls(dict(), **kwargs)

    @singledispatchmethod
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
        except (ValueError, TypeError) as e:
            logger.warning(f"Units from any failed on from_string for input: {other}.  Failure was: {e}")   

        try: # dictionary like?
            len(other) #type: ignore
            other.keys() #type: ignore
            other.items() #type: ignore
            return cls(other) #type: ignore
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Unable to make new unit from {other}")
            raise TypeError(f"Unable to make new unit from {other}.  Original exception was {e}")

    @from_any.register
    @classmethod
    def _(cls, other: str):
        return cls.from_string(other)
    
    @from_any.register
    @classmethod
    def _(cls, other: OptionsConfigParameter):
        return cls.from_string(other.parameter)

    @classmethod
    def from_string(cls, ustring : str, **kwargs) -> t_UnitObj:
        """
        Creates a Unit object from a string representation.

        :param ustring: units strng
        :return: new Units instance
        :raises TypeError: if input is not string type
        :raises ValueError: if ustring cannot be split cleanly
        """

        # hanging dots are tricky... remove them with a regex... maybe we can algo our way out of it later.
        def group_replace(match):
            group_text = match.group(0)
            return group_text.replace(".", "")
        ustring_clean = re.sub(r"(?:\()(\.+)|(\.+)(?:\))", group_replace, ustring)
        

        ndparts1 = ustring_clean.split("/") # get num/den parts (can be any number... a/b/c)
        if cls.__DEBUG:
            ndparts2 = [nd.split(".") for nd in ndparts1] # each elemnent is split by a dot
            ndparts3 = [[ep.split("^") for ep in np] for np in ndparts2] # 
        else:
            ndparts2 = (nd.split(".") for nd in ndparts1) # each elemnent is split by a dot
            ndparts3 = ((ep.split("^") for ep in np) for np in ndparts2) # 

        sdict = {}
        group_sets = [-1]
        sign_normal = 1
        for numden in ndparts3:
            group_sets[-1] = -1*group_sets[-1]
            for element in numden:
                try:
                    base, exp = element
                except ValueError:
                    base, exp = (element[0], 1)

                if cls.__DEBUG:
                    logger.error(f"Converting {ustring}:\n" +
                                "\n".join(f"{s:15}:{list(o)}" for s, o in {"element": element, "numden": numden, 
                                                                    "ndparts3": [list(o2) for o2 in ndparts3]}.items()))
                    logger.error(f"Currently at\n\tgroup_sets: {group_sets}\n\tsign_normal: {sign_normal}\n\tsdict: {sdict}")
                
                try: # ugly but... way shorter than cathing it all.  this works fine for debugging.
                    if base == "":
                        pass # skip if empty
                    elif base[0] == "(": # starting a group
                        # case:       ?(###... starts a new group in any case
                        #       ...###/(###... sets 'hold' on a negative sign exponent (set normal to -1)
                        base_clean = base[1:]
                        if element[-1][-1] == ")": # ending a group, start and end... same as NONE
                            if group_sets[-1] + sign_normal: # we are the normal sign... 
                                this_exp = sign_normal
                            else: # we are not sign normal... must be first after a change. re-set to sign normal after use.
                                this_exp = group_sets[-1]
                                group_sets[-1] = sign_normal
                            try:
                                exp_int = int(exp[:-1]) # type: ignore , if it existed, its a string << NOT SAME AS NONE
                                base_cleaner = base_clean
                            except TypeError as e:
                                exp_int = int(exp)
                                base_cleaner = base_clean[:-1] # ugly reset but... meh
                            sdict[base_cleaner] = sdict.get(base_cleaner, 0) + exp_int*this_exp
                        else:
                            sign_normal = group_sets[-1] # if it was negative, new normal is... otherwise not.
                            group_sets.append(sign_normal) # start a new group
                            exp_int = int(exp)
                            sdict[base_clean] = sdict.get(base_clean, 0) + exp_int*sign_normal # really last element, but thats set here.                
                    elif element[-1][-1] == ")": # ending a group
                        sign_normal = 1 # if we were negative, its positive now. if we were positive, keep it.
                        this_exp = group_sets.pop() # this is the last element with the prev sign... maybe
                        try:
                            exp_int = int(exp[:-1]) # type: ignore , if it existed, its a string << NOT SAME AS NONE
                            base_clean = base
                        except TypeError as e:
                            exp_int = int(exp)
                            base_clean = base[:-1] # ugly reset but... meh
                        sdict[base_clean] = sdict.get(base_clean, 0) + exp_int*this_exp
                    else: # same group
                        # this a x: ##x#     stays normal.  maybe -1 if in a group that set that... 
                        #           ###/x##  
                        # normal is unchanged, but first item is "not normal"
                        #           ###/#x##
                        #           ###/##x#
                        if group_sets[-1] + sign_normal: # we are the normal sign... 
                            this_exp = sign_normal
                        else: # we are not sign normal... must be first after a change. re-set to sign normal after use.
                            this_exp = group_sets[-1]
                            group_sets[-1] = sign_normal
                        exp_int = int(exp)
                        sdict[base] = sdict.get(base, 0) + exp_int*this_exp
                except (ValueError, TypeError) as e:
                    raise UnitsConstructionException(ustring, (element, element[-1][-1], numden, ndparts3), msg=f"Original error: {e}")
                if cls.__DEBUG:
                    logger.error(f"After loop... at\n\tgroup_sets: {group_sets}\n\tsign_normal: {sign_normal}\n\tsdict: {sdict}")

        _ = sdict.pop("1", None) # remove ones as a base.. 
        _ = sdict.pop("", None) # remove empty as a base.. 
        sdict_clean = {k: v for k, v in sdict.items() if v}
        obj = cls(sdict_clean, **kwargs)
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
        ns = self.s.copy() # dictionary, so copy it
        nc = self.context # string, no need to copy
        return type(self)(s=ns, context=nc)

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