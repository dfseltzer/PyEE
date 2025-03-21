from pyee import units

u_force = units.Units.from_string("kg.m/s^2")
u_accel = units.Units.from_string("m/s^2")
u_mass  = units.Units.from_string("kg")

print(f"Mass * Accel = {u_accel*u_mass}")
print(f"Force / Accel = {u_force/u_accel}")

