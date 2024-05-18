"""
This example shows you how to produce NetCDF files to help visualize the smoke in-line 
point sources on the CMAQ model grid.

Since this example submits a job to the slurm scheduler, there's no need to run this 
inside a tmux window.
"""

from cmaqpy.runsmoke import SMOKEModel

# Specify the date
date = '2016-08-11'

# Specify the sector
sector = 'ptertac'
# sector = 'ptertac_s0'

# Specify if you want to run the 12 km or the 4 km domain
appl = '2016Base_12OTC2'
# appl = '2016_12OTC2'
# appl = '2016Base_4OTC2'
# appl = '2016_4OTC2'
if appl == '2016_12OTC2':
    grid_name = '12OTC2' 
elif appl == '2016Base_12OTC2':
    grid_name = '12OTC2'
elif appl == '2016_4OTC2':
    grid_name = '4OTC2' 
elif appl == '2016Base_4OTC2':
    grid_name = '4OTC2'

# Create a CMAQModel object
smoke_sim = SMOKEModel(appl, grid_name, sector=sector, setup_yaml=f'dirpaths_{appl}.yml', verbose=True)
# Call the "run_inlineto2d" method
smoke_sim.run_inlineto2d(date, run_hours=1, mem_per_node=20)
