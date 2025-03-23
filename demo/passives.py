from pyee.units import PhysicalQuantity
from pyee.passives import Resistor, Inductor, Capacitor

R1 = Resistor(1000)
R2 = Resistor(125)
print(f"{R1} + {R2} = {R1+R2}")

print(f"Base units for R1: {R1.as_base().u}")