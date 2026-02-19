
import re
import logging

from pyee.types.units import Units
from pyee.types.aliases import t_numeric
from pyee.types.prefixes import Prefix, t_PrefixObj

from pyee.regex import re_number_and_prefix

logger = logging.getLogger(__name__)

def vp_from_number(number: t_numeric) -> tuple[t_numeric, t_PrefixObj]:
    """
    Converts a numeric value to a tuple containing the scaled value and its corresponding prefix object.

    Args:
        number (t_numeric): The numeric value to be converted.

    Returns:
        tuple[t_numeric, t_PrefixObj]: A tuple where the first element is the scaled value (number divided by the prefix factor),
        and the second element is the prefix object representing the scaling factor.

    Example:
        >>> vp_from_number(1000)
        (1.0, Prefix('kilo', 'k', 1000))
    """
    p = Prefix.from_number(number)
    v = number/p.f # avoid python calling __rdiv__ on each element for lists
    return v, p

def vpu_from_ustring(ustring : str) -> tuple[t_numeric, "Prefix", "Units"]:
    """
    Converts a unit string into a tuple of (value, prefix, unit).
    This function parses a string representing a value with an optional SI prefix and unit,
    and returns a tuple containing the numeric value, a Prefix instance, and a Units instance.
    Examples:
        "10uH"   -> (10, <Prefix 'u'>, <Units 'H'>)
        "100"    -> (100, <Prefix ''>, <Units ''>)
        "1.23p F"-> (1.23, <Prefix 'p'>, <Units 'F'>)
    Accepted formats:
          (No spaces, any valid Python float or int)
        - Numbers with prefix: "100u" or "1.23p"
          (No space between number and prefix, standard SI prefixes only)
        - Numbers with prefix and unit: "100u H", "1.23p F"
          (Space between prefix and unit, no space between number and prefix, standard SI prefixes only)
    Args:
        ustring (str): The input string to parse.
    Returns:
        tuple[t_numeric, Prefix, Units]: A tuple containing the numeric value, Prefix instance, and Units instance.
    Raises:
        ValueError: If the input string cannot be parsed into a value, prefix, and unit.
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
    units = Units(parts[1] if len(parts) == 2 else "")

    return val_u, prefix_u, units
