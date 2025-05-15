"""
A collection of generally useful python helper, wrapers, and other things for engineering.  Relies on Numpy for a bunch
of stuff, either using directly or preferably adding wrappers to make things easier.
"""

__version__ = "2025.0.1"

import logging
from .utilities import CustomFormatter

GLOBAL_TOLERANCE = 1e-15

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
