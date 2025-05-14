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
