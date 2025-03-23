"""
Passive component types
"""

from .units import PhysicalQuantity

class Resistor(PhysicalQuantity):
    def __init__(self, value):
        super().__init__(value=value, units="Ohm")

class Inductor(PhysicalQuantity):
    def __init__(self, value):
        super().__init__(value=value, units="H")

class Capacitor(PhysicalQuantity):
    def __init__(self, value):
        super().__init__(value=value, units="F")
