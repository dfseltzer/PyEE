from pyee import types

u_force = types.units.from_string("kg.m/s^2")
u_accel = types.units.from_string("m/s^2")
u_mass  = types.units.from_string("kg")

print(f"Mass * Accel = {u_accel*u_mass}")
print(f"Force / Accel = {u_force/u_accel}")

