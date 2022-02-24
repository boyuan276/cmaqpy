"""
This example shows how to update the calc_hourly_base.csv emissions file 
that is output from the ERTAC EGU preprocessor. This file hold the CAMD 
CEMS data for all EGUs in the US (or a subregion if you have subsetted the file).

Take more than for hours on a high-memory node to run this one -- I think because the
dataset takes up so much memory... could defitiely improve this... so definitely run
this via an interactive job and not on the head node.
"""

from cmaqpy.prepemis import update_camd

# Define the paths to data files containing the base emissions, the new emissions  
# predictions, the generation of each egu, the lookup table holding the NYISO to 
# CAMD ID conversion information, and the name for the update emissions file.
in_emis_file = '/home/jas983/models/ertac_egu/CONUS2016_S0/inputs/calc_hourly_base.csv'
co2_file = '../cmaqpy/data/ny_emis/ml_output/pred_xg_co2.csv'
nox_file = '../cmaqpy/data/ny_emis/ml_output/pred_xg_nox.csv'
so2_file = '../cmaqpy/data/ny_emis/ml_output/pred_xg_so2.csv'
gen_file = '../cmaqpy/data/ny_emis/ed_output/thermal_with_renewable_20160805_20160815.csv'
lu_file = '../cmaqpy/data/ny_emis/ed_output/RGGI_to_NYISO.csv'
out_emis_file = '/home/jas983/models/ertac_egu/CONUS2016_S0/inputs/updated_calc_hourly_base.csv'

update_camd(in_emis_file=in_emis_file, co2_file=co2_file, 
            nox_file=nox_file, so2_file=so2_file, 
            gen_file=gen_file, lu_file=lu_file, 
            out_emis_file=out_emis_file)