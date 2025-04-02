from pyee.types.units import Units

u_force = Units.from_string("kg.m/s^2")
u_accel = Units.from_string("m/s^2")
u_mass  = Units.from_string("kg")

print(f"Mass * Accel = {u_accel*u_mass}")
print(f"Force / Accel = {u_force/u_accel}")

u_v = Units.from_string("V")
u_a = Units.from_string("A")

# simplify is best from base units
print(f"Ohms: {u_v/u_a} = {(u_v/u_a).as_base()} = {(u_v/u_a).as_base().simplify()})")

