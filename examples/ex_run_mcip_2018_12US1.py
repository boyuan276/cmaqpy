"""
This example shows how to process wrfout files with MCIP using the `CMAQModel` class.

Note that MCIP will fail if your `start_datetime` is not AFTER the fist timestep of 
your wrfout*.nc file.
"""

import os
from cmaqpy.runcmaq import CMAQModel

start_datetime = "2018-04-21"  # first day that you want processed
end_datetime = "2018-05-01"  # ONE DAY AFTER the last day you want processed

# Specify if you want to run the 12 km or the 4 km domain
appl = "2018_12US1"

# Define the coordinate name (must match that in GRIDDESC)
if "2018_12US1" in appl:
    coord_name = "LAM_40N97W"
    grid_name = "12US1"
else:
    raise ValueError(f"Unknown application: {appl}")

# Create a CMAQModel object
cmaq_sim = CMAQModel(
    start_datetime,
    end_datetime,
    appl,
    coord_name,
    grid_name,
    setup_yaml=f"dirpaths_{appl}.yml",
    new_mcip=True,
    new_icon=False,
    new_bcon=False,
    verbose=True,
)

# Specify the meteorolocial files
metfile_dir = "/mnt/Bo_HDD4/wrf_data/met4ene/wrfout/ARW/2018-04-20_8mp4lw2sw2lsm5pbl3cu"
assert os.path.exists(metfile_dir), f"Directory {metfile_dir} does not exist!"
metfile_list = [
    "wrfout_d01_2018-04-20_00:00:00",
]

# Call the "run_mcip" method
cmaq_sim.run_mcip_multiday(
    metfile_dir=metfile_dir,
    metfile_list=metfile_list,
    geo_file="geo_em.d01.nc",
    t_step=60,
    setup_only=False
)
