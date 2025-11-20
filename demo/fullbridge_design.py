from pyee.smps.fullbridge import FullBridgeFixedFrequency

SMPS = FullBridgeFixedFrequency(fs="100k", L="33u")

ilm_pk = SMPS.ilm_pk({"vin":100, "D":0.2})
print(ilm_pk)