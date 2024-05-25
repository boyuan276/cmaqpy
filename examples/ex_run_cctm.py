"""
This example shows how to run the CCTM benchmark case using the `CMAQModel` class.

You should run this inside a tmux window because this ties up the terminal.
"""

from cmaqpy.runcmaq import CMAQModel

# Specify the start/end times
start_datetime = 'August 06, 2016'  # first day that you want run
end_datetime = 'August 14, 2016'  # DAY AFTER the last day you want run

# Specify if you want to run the 12 km or the 4 km domain
# appl = '2016_12OTC2'
appl = '2016Base_12OTC2'
# appl = '2016_4OTC2'
# appl = '2016Base_4OTC2'

# Specify if you want to run or just setup cctm
setup_only = False

# Define the coordinate name (must match that in GRIDDESC)
coord_name = 'LAM_40N97W'
if appl == '2016_12OTC2':
    grid_name = '12OTC2'
elif appl == '2016Base_12OTC2':
    grid_name = '12OTC2'
elif appl == '2016_4OTC2':
    grid_name = '4OTC2'
elif appl == '2016Base_4OTC2':
    grid_name = '4OTC2'

new_mcip = False  # Use existing MCIP data

if grid_name == '12OTC2':
    # Create a CMAQModel object.
    # Note that we use exiting BCON data, so we set new_bcon=False.
    cmaq_sim = CMAQModel(start_datetime, end_datetime,
                         appl, coord_name, grid_name,
                         chem_mech='cb6r5_ae7_aq',
                         cctm_vrsn='v54',
                         setup_yaml=f'dirpaths_{appl}.yml',
                         compiler='gcc',
                         compiler_vrsn='11.3.0',
                         new_mcip=new_mcip,
                         new_icon=False, icon_vrsn='v54',
                         new_bcon=False, bcon_vrsn='v54',
                         verbose=True)
    # Call the "run_cctm" method
    cmaq_sim.run_cctm(n_emis_gr=2, gr_emis_labs=['all', 'rwc'], n_emis_pt=9,
                      pt_emis_labs=['ptnonertac', 'ptertac', 'othpt', 'ptagfire',
                                    'ptfire', 'ptfire_othna', 'pt_oilgas', 'cmv_c3_12', 'cmv_c1c2_12'],
                      stkgrps_daily=[False, False, False, True,
                                     True, True, False, False, False],
                      ctm_abflux='Y',
                      stkcaseg='12US1_2016fh_16j', 
                      stkcasee='12US1_cmaq_cb6_2016fh_16j',
                      delete_existing_output='TRUE', 
                      new_sim='FALSE', tstep='010000',
                      cctm_hours=24, n_procs=48, gb_mem=50, 
                      run_hours=72, setup_only=False)
elif grid_name == '4OTC2':
    # Create a CMAQModel object
    cmaq_sim = CMAQModel(start_datetime, end_datetime,
                         appl, coord_name, grid_name,
                         chem_mech='cb6r5_ae7_aq',
                         cctm_vrsn='v54',
                         setup_yaml=f'dirpaths_{appl}.yml',
                         compiler='gcc',
                         compiler_vrsn='11.3.0',
                         new_mcip=True,
                         new_icon=False, icon_vrsn='v54',
                         new_bcon=True, bcon_vrsn='v54',
                         verbose=True)
    # Call the "run_cctm" method
    # Note that we turn off the ammonia bi-directional flux for in-line deposition (ctm_abflux='N') for the 4km domain
    cmaq_sim.run_cctm(n_emis_gr=3, gr_emis_labs=['all', 'rwc', 'beis'], n_emis_pt=7,
                      pt_emis_labs=['ptnonertac', 'ptertac', 'ptagfire',
                                    'ptfire', 'pt_oilgas', 'cmv_c1c2_4', 'cmv_c3_4'],
                      stkgrps_daily=[False, False, True,
                                     True, False, False, False],
                      ctm_abflux='N',
                      stkcaseg='12US1_2016fh_16j', 
                      stkcasee='12US1_cmaq_cb6_2016fh_16j',
                      delete_existing_output='TRUE', 
                      new_sim='FALSE', tstep='010000',
                      cctm_hours=24, n_procs=48, gb_mem=50, 
                      run_hours=72, setup_only=False)
