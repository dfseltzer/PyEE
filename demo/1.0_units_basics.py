"""
This demo showcases the basic functionality of the Units class, which is the
foundation for handling physical units within the PyEE library.
"""

from pyee.types.units import Units

# 1. Construction
# The Units class can be instantiated directly from strings, dictionaries, or None.
print("--- 1. Construction ---")
u_force = Units("kg.m/s^2")  # From a complex string
u_accel = Units("m/s^2")
u_mass = Units("kg")
u_unitless = Units(None)      # A unitless instance

print(f"Force units: {u_force}")
print(f"Acceleration units: {u_accel}")
print(f"Is '{u_unitless}' unitless? {'Yes' if not u_unitless else 'No'}")
print("-" * 20)

# 2. Mathematical Operations
# Units can be multiplied, divided, and compared intuitively.
print("--- 2. Mathematical Operations ---")
u_derived_force = u_mass * u_accel
print(f"Multiplying units: {u_mass} * {u_accel} = {u_derived_force}")
print(f"Are the results equal to the force unit? {u_derived_force == u_force}")

u_derived_mass = u_force / u_accel
print(f"Dividing units: {u_force} / {u_accel} = {u_derived_mass}")
print(f"Are the results equal to the mass unit? {u_derived_mass == u_mass}")
print("-" * 20)

# 3. Simplification and Context
# The class can simplify complex base units into derived units.
print("--- 3. Simplification and Context ---")
u_volts = Units("V")
u_amps = Units("A")

# First, expand the derived units to their base representation
u_ohms_base = (u_volts / u_amps).as_base()
print(f"Ohms ({u_volts}/{u_amps}) in base units: {u_ohms_base}")

# Now, simplify the base representation back into the derived unit
u_ohms_simplified = u_ohms_base.simplify()
print(f"Simplifying '{u_ohms_base}' back to a derived unit: {u_ohms_simplified}")
print("-" * 20)

# 4. Numerator and Denominator
# You can inspect the numerator and denominator of a complex unit.
print("--- 4. Numerator and Denominator ---")
print(f"For the force unit '{u_force}':")
print(f"  Numerator is: {u_force.n}")
print(f"  Denominator is: {u_force.d}")
print("-" * 20)
