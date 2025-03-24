"""
Passive component types
"""

from .units import PhysicalQuantity

class PassiveComponent(PhysicalQuantity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # add parallel operation
    def __or__(self, other):
        return self * other / (self + other)

    def __ror__(self, other):
        return other * self / (other + self)

class Resistor(PassiveComponent):
    def __init__(self, value):
        super().__init__(value=value, units="Ohm")

class Inductor(PassiveComponent):
    def __init__(self, value):
        super().__init__(value=value, units="H")

class Capacitor(PassiveComponent):
    def __init__(self, value):
        super().__init__(value=value, units="F")
