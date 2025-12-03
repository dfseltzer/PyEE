"""
Full Bridge Converters.  These converters use the following standard names...
- v1 and v2: input and output voltages, with associated i1 and i2.  Note that for power flow from
v1 to v2, both i1 and i2 are positive.
- lm: magnetizing inductor, with current ilm
- l1: main energy storage inductor, with current il1 (=i2 in most cases)
- N: primary to secondary turns ratio, Np/Ns.  For example, for a 2:1:1 transformer, N=2
"""


from .smps import FixedFrequencySMPS, format_fs
from ..passives import Inductor
from ..types.physicalquantity import PhysicalQuantity
from ..types.physicalquantity import value_from_any
from ..types.decorators import state_check

from enum import Enum

import numpy as np

def FullBridge(fbtype, *args, **kwargs):
    if fbtype is FullBridgeTypes.FixedFrequency:
        return FullBridgeFixedFrequency(*args, **kwargs)
    else:
        raise TypeError(f"Unknown Buck converter asked for: {fbtype}")

class FullBridgeTypes(Enum):
    FixedFrequency = 1

class FullBridgeFixedFrequency(FixedFrequencySMPS):

    _defaults = {"fs_units": "Hz"}

    @classmethod
    def D_from_v1_v2(self, v1, v2, N=1):
        """
        D value for v2, given v1
        """
        return v2/(N*v1)

    def __init__(self, fs, L, N=1, **kwargs) -> None:
        """
        :param fs: Switching frequency
        :param L: Primary unductance value, in Henries
        :param fs_units: optional, fs_units to use. If none, defaults to class default.
        """
        fs = format_fs(inputobj=fs, defaultunits=self._defaults["fs_units"], 
                       inputunits=kwargs.pop("fs_units", None))
        super().__init__(fs, **kwargs)

        if isinstance(L, Inductor):
            self.L = L.copy()
        else:
            self.L = Inductor.from_string(L)
        self.N = N
        self.state = {"v1": None, "D": None, "i2": None}

    @state_check ("v1", "D")
    def ilm_pk(self, state=None):
        """
        peak magnetizing current
        v = L*di/dt -> di = v*dt/L -> ilm_pk = v*(D*Ts)/(2*L)
        """
        assert isinstance(state, dict)
        val = np.divide(state["v1"]*state["D"]*self.Ts.value, 2*self.L.value)
        return PhysicalQuantity.from_value(val, "A")

    @state_check("v1", "D")
    def v2(self,state=None):
        """
        output incuctor ripple amplitude - peak to peak value.
        dil = (N Vp - Vs)*D*Ts/L
        """
        assert isinstance(state, dict)
        val = state["v1"]*self.N*state["D"]
        return PhysicalQuantity.from_value(val, "V")

    @state_check("v1", "D", "i2")
    def i2_pk(self, state=None):
        """
        output peak value
        """
        assert isinstance(state, dict)
        i2_pkpk = self._i2_pkpk(state["D"], state["v1"])
        val = state["i2"]+i2_pkpk/2
        return PhysicalQuantity.from_value(val, "A")

    @state_check("v1", "D")
    def i2_pkpk(self,state=None):
        """
        output ripple amplitude - peak to peak value.
        """
        assert isinstance(state, dict)
        return self._i2_pkpk(state["D"], state["v1"])
    
    def _i2_pkpk(self, d, v1):
        #TODO implement helpers like this for all methods that are used by others to speed up execution.
        D2 = np.square(d)
        val = (self.N*(d - D2)*self.Ts*v1)/self.L
        return PhysicalQuantity.from_value(val, "A")

    @state_check("v1", "D", "i2")
    def i2_rms(self, state=None):
        """
        RMS output current
        """
        assert isinstance(state, dict)
        i2ac_rms = self._i2_pkpk(state["D"], state["v1"])*np.sqrt(3)
        i2ac_rms2 = np.square(i2ac_rms)
        i2dc_rms2 = np.square(state["i2"])
        sqrsum = i2ac_rms2 + i2dc_rms2
        val = np.sqrt(sqrsum)
        return PhysicalQuantity.from_value(val, "A")

    @state_check("v1", "D", "i2")
    def ip_pk(self, state=None):
        """
        Transformer primary peak current
        """
        assert isinstance(state, dict)
        return self.i2_pk(state=state)/self.N

    @state_check("v1", "D", "i2")
    def ip_rms(self, state=None):
        """
        Transformer primary peak current
        """
        assert isinstance(state, dict)
        di2 = self._i2_pkpk(state["D"], state["v1"])/2
        radicand = 3*np.square(state["i2"]) + np.square(di2)
        val = np.sqrt(radicand)/(self.N * np.sqrt(6))
        return PhysicalQuantity.from_value(val, "A")

    @state_check("v1", "D", "i2")
    def is1_pk(self, state=None):
        """
        split secondary 1 peak current
        """
        return self.i2_pk(state=state)
    
    @state_check("v1", "D", "i2")
    def is1_rms(self, state=None):
        """
        split secondary 1 rms current
        """
        assert isinstance(state, dict)
        i2 = state["i2"]
        di2 = self._i2_pkpk(state["D"], state["v1"])/2
        radican = 3*np.square(i2) - 8*di2*i2 + 9*np.square(di2)
        val = np.sqrt(radican)/np.square(2)
        return PhysicalQuantity.from_value(val, "A")

    @state_check("v1", "D", "i2")
    def is2_pk(self, state=None):
        """
        split secondary 2 peak current
        """
        return self.i2_pk(state=state)
    
    @state_check("v1", "D", "i2")
    def is2_rms(self, state=None):
        """
        split secondary 1 rms current
        """
        assert isinstance(state, dict)
        return self.is1_rms(state=state)