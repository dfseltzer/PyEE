"""
Buck Converter
"""

from .smps import FixedFrequencySMPS
from ..passives import Inductor

from enum import Enum

def Buck(bucktype, *args, **kwargs):
    if bucktype is BuckTypes.FixedFrequency:
        return BuckFixedFrequency(*args, **kwargs)
    else:
        raise TypeError(f"Unknown Buck converter asked for: {bucktype}")

class BuckTypes(Enum):
    FixedFrequency = 1

class BuckFixedFrequency(FixedFrequencySMPS):
    def __init__(self, fs, L, fs_units="Hz"):
        super().__init__(fs, "fs_units")
        self.L = Inductor(L)

    