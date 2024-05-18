"""
This example shows how to process wrfout files with MCIP using the `CMAQModel` class.

Note that MCIP will fail if your `start_datetime` is not AFTER the fist timestep of 
your wrfout*.nc file.
"""

from cmaqpy.runcmaq import CMAQModel

start_datetime = 'August 06, 2016'  # first day that you want processed
end_datetime = 'August 15, 2016'  # ONE DAY AFTER the last day you want processed
# Specify if you want to run the 12 km or the 4 km domain
# appl = '2016_12OTC2'
appl = '2016_4OTC2'
coord_name = 'LAM_40N97W'
if appl == '2016_12OTC2':
    grid_name = '12OTC2'
elif appl == '2016_4OTC2':
    grid_name = '4OTC2'

# Create a CMAQModel object
cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name, 
    setup_yaml=f'dirpaths_{appl}.yml', verbose=True)
# Specify the meteorolocial files
if appl == '2016_12OTC2':
    metfile_list = ['wrfout_d01_2016-08-05_00:00:00']
elif appl == '2016_4OTC2':
    metfile_list = ['wrfout_d02_2016-08-05_00:00:00']
# Call the "run_mcip" method 
if appl == '2016_12OTC2':
    cmaq_sim.run_mcip_multiday(metfile_dir=None, metfile_list=metfile_list, geo_file='geo_em.d01.nc', t_step=60)
elif appl == '2016_4OTC2':
    cmaq_sim.run_mcip_multiday(metfile_dir=None, metfile_list=metfile_list, geo_file='geo_em.d02.nc', t_step=60)
