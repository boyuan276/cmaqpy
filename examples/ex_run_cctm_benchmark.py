"""
This example shows how to run the CCTM benchmark case using the `CMAQModel` class.
"""

from cmaqpy.runcmaq import CMAQModel

start_datetime = 'July 01, 2016'
end_datetime = 'July 02, 2016'
appl = '2016_12SE1'
coord_name = 'LamCon_40N_97W'
grid_name = '2016_12SE1'

# Create a CMAQModel object
cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name, verbose=True)
# Call the "run_cctm" method
cmaq_sim.run_cctm(cctm_vrsn='v533', delete_existing_output='TRUE', new_sim='TRUE', tstep='010000', n_procs=16, run_hours=24,setup_only=False)
