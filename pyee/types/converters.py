
import re

from .units import Units
from .prefixes import Prefix

from ..regex import re_number_and_prefix

def vp_from_number(number):
    """
    Convert a number to a value an prefix
    """
    p = Prefix.from_number(number)
    v = 1/p * number # avoid python calling __rdiv__ on each element for lists
    return v, p

def vpu_from_ustring(ustring):
    """
    Convert a unit string into [Value, Prefix, Unit] set
    For example,       10uH =  [10,       <u>,  <H>], where <u> is a Prefix instance,
    and <H> is a Unit instance.

    Strings that will work well include...
        - Numbers: "100" or "1.23"
        -- Include no spaces
        -- Anything python can convert into an integer or float will work
        - Numbers with a prefix: "100u" or "1.23p"
        -- Standard SI prefixes only
        -- Do not include a space between prefix and number
        - Numbers with a prefix and unit: "100u H", "1.23p F"
        -- Standard SI prefixes only
        -- Do not include a space between prefix and number
        -- Include a space between prefix and units
        -- Any unit that the Unit class can parse will work

    Returns: New physical quantity from string
    """

    parts = ustring.split(" ")
    if len(parts) > 2:
        raise ValueError(f"Unable to convert string into Float, Prefix, Units set: {ustring}.  Too many parts?")
    
    valprevix_match = re_number_and_prefix.fullmatch(parts[0])

    if valprevix_match is None:
        raise ValueError(f"Unable to convert string into Float, Prefix, Units set: {ustring}.  Bad format?")

    val_s = valprevix_match.group("number")
    prefix_s = valprevix_match.group("prefix")

    val = float(val_s)
    prefix = Prefix(prefix_s)

    units = Units.from_string(parts[1] if len(parts) == 2 else "")
    return val, prefix, units
