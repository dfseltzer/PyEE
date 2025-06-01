
import re
import logging

from pyee.types.units import Units
from pyee.types.aliases import t_numeric
from pyee.types.prefixes import Prefix, t_PrefixObj

from pyee.regex import re_number_and_prefix

logger = logging.getLogger(__name__)

def vp_from_number(number: t_numeric) -> tuple[t_numeric, t_PrefixObj]:
    """
    Convert a number to a value an prefix
    """
    p = Prefix.from_number(number)
    v = number/p.f # avoid python calling __rdiv__ on each element for lists
    return v, p

def vpu_from_ustring(ustring : str) -> tuple[t_numeric, "Prefix", "Units"]:
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

    Returns: [Value, Prefix, Unit]
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
    prefix = Prefix.from_string(prefix_s)
    val_u, prefix_u = Prefix.rebalance(val, prefix)
    units = Units.from_string(parts[1] if len(parts) == 2 else "")

    return val_u, prefix_u, units
