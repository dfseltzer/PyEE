__version__ = "2025.0.1"

import logging
from .utilities import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
