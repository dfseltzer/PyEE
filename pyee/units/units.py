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

logger = logging.getLogger(__name__)

class PhysicalQuantity:
    def __init__(self, value=None, units=None):
        self.__v = value
        self.__u = units


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
        s_full = [(ue0, int(ue1)) for ue0, ue1 in u_parts]
        logger.debug(f"Converter {ustring} in to {s_full}")

        obj = cls()
        obj.s = s_full
        obj.cancel()

        return obj

    def __init__(self):
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

        Stored internally as one array (s) using negative exponents
        """
        self.s = [("1",1),]

    def cancel(self):
        """
        Cancels units where possible.  Does not expand before canceling.
        :return: None
        """
        olen = len(self.s)
        uparts = set(u for u, e in self.s)
        if len(uparts) == olen:
            logger.debug(f"Nothing to cancel > {self.s}")
            return

        ucount = {v: sum([e for u, e in self.s if u==v]) for v in uparts}
        self.s = [(v, e) for v, e in ucount.items() if e != 0]
        logger.debug(f"Canceled {olen-len(self.s)} > {self.s}")


    def n(self):
        """
        Numerator sets
        :return: n = [(s, e), ...]
        """
        return [(s, e) for s, e in self.s if e > 0]

    def d(self):
        """
        Denominator sets
        :return: d = [(s, e), ...]
        """
        return [(s, -e) for s, e in self.s if e < 0]