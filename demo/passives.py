
from pyee.passives import Resistor, Inductor, Capacitor

R1 = Resistor(1000)
R2 = Resistor(125)

C1 = Capacitor(1e-6)

print(f"{R1} + {R2} = {R1+R2}")

print(f"Trying to add R1 = {R1} to C1 = {C1}")
try:
    Z1 = R1+C1
except TypeError as e:
    print(f"Failed with: {e}")
else:
    print(f"Success? Z1 = {Z1}")

R1_base = R1.as_base()
print(f"R1 in base units: R1_base = {R1_base}")

R1_simple = R1_base.simplify()
print(f"R1_base simplified again: R1_simple = {R1_simple}")

R3 = R1 | R2
print(f"R1 ({R1}) | R2 ({R2}) = ({R3})")

Z1 = R3 | C1
print(f"R3 ({R3}) | C1 ({C1}) = ({Z1})")
