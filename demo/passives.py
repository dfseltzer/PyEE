
import pyee
import pyee.exceptions
from pyee.passives import Resistor, Capacitor
import pyee.passives

pyee.logger.setLevel(level=20) # info
#pyee.logger.setLevel(level=50) # above error... basically off...

R1 = Resistor.from_value(1000)
R2 = Resistor.from_value(125)
C1 = Capacitor.from_value(1e-6)

print(f"Resistor Addition: {R1} + {R2} = {R1+R2}")
print(f"Trying to add R1 = {R1} to C1 = {C1}")
try:
    Z1 = R1+C1
except pyee.exceptions.UnitsMissmatchException as e:
    print(f">> Failed with: {e}")
else:
    print(f">> Success? Z1 = {Z1}")

R1_base = R1.as_base()
print(f"R1 in base units (context is {R1.u.context}): R1 = {R1_base}")
print(f"R1 in base units simplified again: R1 = {R1_base.simplify()}")

R3 = R1 | R2
print(f"R3 = R1 ({R1}) | R2 ({R2}) = ({R3})")

# allow addition of non-like units as impedances,
pyee.passives.set_error_on_z_transform(False)

Z0 = R3 + C1
print(f"Z0 = R3 ({R3}) + C1 ({C1}) = ({Z0})")

Z1 = R3 | C1
print(f"Z1 = R3 ({R3}) | C1 ({C1}) = ({Z1})")
print(f"Simplify(Z1) = {Z1.simplify()}")

Z2 = R1 + C1
print(f"Z2 = R1 + C1 = {Z2}")

Z3 = Z2 - C1
print(f"Z3 = Z2 - C1 = R1 = {Z3} = {Z3.simplify()} = {R1}")

Z4 = (Z2 + C1).simplify()
print(f"Z4 = Z2 + C1 = {Z4}")
