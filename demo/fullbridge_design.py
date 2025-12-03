from pyee.smps.fullbridge import FullBridgeFixedFrequency

VIN = 120
VOUT = 30
IOUT = 1000/VOUT

SMPS = FullBridgeFixedFrequency(fs="100k", L="33u", N=2)

default_state = {"v1":VIN, 
                 "i2":IOUT,
                 "D": SMPS.D_from_v1_v2(VIN, VOUT, SMPS.N)}
SMPS.set_state(default_state)

print(f"D for {VIN}:{VOUT} (N={SMPS.N}) is {SMPS.D}")

ilm_pk = SMPS.ilm_pk(state=default_state) # do this if want to give explicit state. Does not change stored state
v2 = SMPS.v2() # do this if want to use stored state.
i2_pkpk = SMPS.i2_pkpk()
i2_pk = SMPS.i2_pk()
i2_rms = SMPS.i2_rms()
is1_rms = SMPS.is1_rms()
ip_pk = SMPS.ip_pk()
ip_rms = SMPS.ip_rms()

print(f"Output Voltage (v2): {v2}")
print(f"Output inductor ripple (i2_pkpk): {i2_pkpk}")
print(f"  ''      ''    peak (i2_pk): {i2_pk}")
print(f"  ''      ''    rms (i2_rms): {i2_rms}")
print(f"Magnetizing Inductor Peak Current (ilm_pk): {ilm_pk}")
print(f"Secondary Tx Inductor RMS (is1_rms): {is1_rms}")
print(f"Primary Tx Inductor peak (ip_pk): {ip_pk}")
print(f"  ''    ''    ''    rms (ip_rms): {ip_rms}")
