"""
Top level classes for switched mode power supplies.
Mostly for inheritance of common items - generally not used by themselves.
"""

import logging
from abc import ABC, abstractmethod

from pyee.types.converters import vpu_from_ustring, vp_from_number

from pyee.types.physicalquantity import PhysicalQuantity, t_PQObj, t_PQSource
from pyee.types.units import Units, t_UnitsSource
from pyee.types.aliases import t_numeric

logger = logging.getLogger(__name__)

def format_fs(inputobj : t_PQSource, defaultunits: t_UnitsSource, inputunits: t_UnitsSource) -> t_PQObj:
    """
    creates a new frequency object, taking into account default units and such.

    unit priority is...
        1. inputunits
        2. defaultunits
        3. inputobj
    if units are unable to be resolve, raises a value exception.

    if a lower priority source has a different unit than a higher priority source, attempts to convert units
    to the higher priority source.  If this fails, raises a unit conversion exception.

    :param inputobj: supplied input object 
    :param defaultunits: default units
    :param inputunits: given fs_units, if any
    """
    
    if isinstance(inputobj, PhysicalQuantity):
        # check units are equal
        # if so, return as is.
        # else, try and convert
        raise NotImplementedError("Write some code...")
    elif isinstance(inputobj, str):
        v, p, u = vpu_from_ustring(inputobj)
    elif isinstance(inputobj, (float, int)):
        v, p = vp_from_number(inputobj)
        u = Units.create_unitless() # empty units
    
    fsobj = PhysicalQuantity(v, p, u)

    if u.unitless: # input obj had no units... use input units if possible, otherwise default
        newu = Units.from_any(inputunits)
        if newu.unitless:
            newu = Units.from_any(defaultunits)
            if newu.unitless:
                raise ValueError(f"Unable to get units for frequency: inobj={inputobj}, defu={defaultunits}, inu={inputunits}")
        fsobj.units = newu # had no units, so skip built in conversion
    else: # we have a unit... see if we need to convert
        newu = Units.from_any(inputunits)
        if newu.unitless: # nope, see if a default was given...
            newu = Units.from_any(defaultunits)
            if newu.unitless: # nope... pass and keep existing units.
                pass
            else: # convert to default units if we can
                fsobj.units = newu
        else: # convert to input units if we can
            fsobj.units = newu

    return fsobj

class FixedFrequencySMPS(ABC, object):
    def __init__(self, fs : t_PQObj, **kwargs) -> None:
        super().__init__()
        self._fs = fs
        self._Ts = 1/self._fs

    @property
    def fs(self):
        return self._fs

    @fs.setter
    def fs(self, val):
        self._fs.value = val
        self._Ts.value = 1/val

    @property
    def Ts(self):
        return self._Ts

    @Ts.setter
    def Ts(self, val):
        self._Ts.value = val
        self._fs.value = 1/val
