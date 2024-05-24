"""
This example shows how to run the CCTM benchmark case using the `CMAQModel` class.

Since this example submits a job to the slurm scheduler, there's no need to run this 
inside a tmux window.
"""

from cmaqpy.runsmoke import SMOKEModel


# Specify if you want to run the 12 km or the 4 km domain
appl = '2016Base_12OTC2'
# appl = '2016_12OTC2'
# appl = '2016Base_4OTC2'
# appl = '2016_4OTC2'

# Select the grid name according to the application
if appl == '2016_12OTC2':
    grid_name = '12OTC2' 
elif appl == '2016Base_12OTC2':
    grid_name = '12OTC2'
elif appl == '2016_4OTC2':
    grid_name = '4OTC2' 
elif appl == '2016Base_4OTC2':
    grid_name = '4OTC2'
    
# Specify if you want to run or just setup cctm
setup_only = False

# Create a CMAQModel object
smoke_sim = SMOKEModel(appl, 
                       grid_name, 
                       sector='ptertac', 
                       run_months=[8], 
                       ertac_case='CONUS2016_Base', # CONUS2016_Base (base case) or CONUS2016_S0 (w/ renewable)
                       emisinv_b='2016fh_proj_from_egunoncems_2016version1_ERTAC_Platform_POINT_calcyear2014_27oct2019.csv', 
                       emisinv_c='egunoncems_2016version1_ERTAC_Platform_POINT_27oct2019.csv', 
                       setup_yaml=f'dirpaths_{appl}.yml', 
                       compiler='gcc', 
                       compiler_vrsn='11.3.0', 
                       smk_exe_str='Linux2_x86_64gfort', 
                       ioapi_exe_str='Linux2_x86_64gfort10',
                       verbose=True)

# Call the "run_sector" method using the "onetime" type
smoke_sim.run_sector(type='onetime', n_procs=1, gb_mem=50, run_hours=12, setup_only=setup_only)
