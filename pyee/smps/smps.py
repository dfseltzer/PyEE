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
    state_variables = []

    def __init__(self, fs : t_PQObj, **kwargs) -> None:
        super().__init__()
        self._fs = fs
        self._Ts = 1/self._fs

        self.state = dict()

    # make sure sub clases define the state variable list...
    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        # Not needed anymore but keep in case... 
        # Check that subclasses define the attribute
        # if "state_variables" not in cls.__dict__:
        #     raise TypeError(
        #         f"Subclass {cls.__name__!r} must define a class attribute 'state_variables'"
        #     )

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

    def state_template(self) -> dict:
        """
        Returns a template state dictionary that can be filled in with values and passed back to 
        functions as needed.
        """
        return {k:None for k in self.state.keys()}

    def update_state(self, newstate):
        """
        Update current state with new state values.  Keep any existing values that do not have new inputs.
        """
        for k, v in newstate.items():
            if k not in self.state:
                logger.warning(f"New state added in update_state?  {k} did not exist.  Adding and setting to {v}")
            self.state[k] = v

    def set_state(self, newstate):
        """
        Replace the current state array with the given one
        """
        for k in self.state.keys():
            if k not in newstate:
                logger.error(f"New state is missing key {k} - this may break your model!")
        
        for k, v in newstate.items():
            if k not in self.state:
                logger.warning(f"New state added in set_state?  {k} did not exist.  Adding and setting to {v}")
            self.state[k] = v

    def __getattr__(self, name):
        """
        Called only if normal attribute lookup fails.
        Try to return from state; otherwise raise AttributeError normally.
        """
        try:
            return self.state[name]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {name!r}")
    
    def __setattr__(self, name, value):
        """
        Called for *all* attribute sets.
        Write to real attributes unless they don't exist,
        in which case write to state.
        """

        # Avoid recursion when initializing 'state'
        if name == "state":
            return super().__setattr__(name, value)

        # Check if state exists, otherwise infinite issues on initialization depending on order we add attributes..
        if "state" in self.__dict__ and name in self.state:
            self.state[name] = value
            return

        # Otherwise store it in the state dictionary
        super().__setattr__(name, value)