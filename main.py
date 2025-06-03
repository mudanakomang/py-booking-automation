#!/home/balisnaptrip/bst/venv/bin/python

from GYG import new_booking as gyg_new, update_booking as gyg_update, cancel_booking as gyg_cancel
from BOKUN import new_booking as bokun_new
from CTRIP import new_booking as ctrip_new
# Call all GYG method
gyg_new()
gyg_update()
gyg_cancel()

# Bokun method
bokun_new()

# Ctrip method
ctrip_new()