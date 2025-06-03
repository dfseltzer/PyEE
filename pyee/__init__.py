"""
A collection of generally useful python helper, wrapers, and other things for engineering.  Relies on Numpy for a bunch
of stuff, either using directly or preferably adding wrappers to make things easier.
"""

__version__ = "2025.0.1"

import logging
from pyee.utilities import CustomFormatter
from pyee.config import NumericConfigParameter, BooleanConfigParameter, OptionsConfigParameter

# Global tolerance used for operations... 
GLOBAL_TOLERANCE = NumericConfigParameter(1e-15)

# Raise an exception when a unitless quantity and a unit-having quantity are 
# used together (for example, 5.0[V/A] + 3.0[unitless]).  Default is FALSE.
ERROR_ON_UNITLESS_OPERATORS = BooleanConfigParameter(False)


# If True, raises an exception when units do not match.  If False, attempts to do the operation
# anyway.  For example, it True, (R1 + C1) would fail.  If False, (R1 + C1) would return a
# frequency dependant impedance object
ERROR_ON_UNIT_MISSMATCH = BooleanConfigParameter(False)

# Default frequency units to use
DEFAULT_FREQUENCY_UNITS = OptionsConfigParameter("Hz", options={"Hz", "Rad"})



logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
