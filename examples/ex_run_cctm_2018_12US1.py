"""
This example shows how to run the CCTM benchmark case using the `CMAQModel` class.

You should run this inside a tmux window because this ties up the terminal.
"""

from cmaqpy.runcmaq import CMAQModel

# Specify the start/end times
start_datetime = "July 02, 2018"  # first day that you want run
end_datetime = "July 03, 2018"  # DAY AFTER the last day you want run

# Specify if you want to run the 12 km or the 4 km domain
appl = "2018_12US1"

# Specify if you want to run or just setup cctm
setup_only = False

# Define the coordinate name (must match that in GRIDDESC)
if "2018_12US1" in appl:
    coord_name = "LAM_40N97W"
    grid_name = "12US1"
else:
    raise ValueError(f"Unknown application: {appl}")

new_mcip = False  # Use existing MCIP data

# Create a CMAQModel object.
# Note that we use exiting BCON data, so we set new_bcon=False.
cmaq_sim = CMAQModel(
    start_datetime,
    end_datetime,
    appl,
    coord_name,
    grid_name,
    chem_mech="cb6r5_ae7_aq",
    cctm_vrsn="v54",
    setup_yaml=f"dirpaths_{appl}.yml",
    compiler="gcc",
    compiler_vrsn="11.3.0",
    new_mcip=new_mcip,
    new_icon=False,
    icon_vrsn="v532",
    new_bcon=False,
    bcon_vrsn="v54",
    verbose=True,
)

# Call the "run_cctm" method
cmaq_sim.run_cctm(
    n_emis_gr=2,
    gr_emis_labs=["all", "rwc"],
    n_emis_pt=10,
    pt_emis_labs=[
        "ptnonipm",
        "ptegu",
        "othpt",
        "ptagfire",
        "ptfire",
        "ptfire_grass",
        "ptfire_othna",
        "pt_oilgas",
        "cmv_c1c2_12",
        "cmv_c3_12",
    ],
    stkgrps_daily=[False, False, False, True, True, True, True, False, False, False],
    ctm_abflux="Y",
    stkcaseg="12US1_WR413_MYR_2018",
    stkcasee="12US1_cmaq_cb6_WR413_MYR_2018",
    delete_existing_output="TRUE",
    new_sim="FALSE",
    tstep="010000",
    cctm_hours=24,
    n_procs=108,
    gb_mem=50,
    run_hours=72,
    setup_only=False,
)
