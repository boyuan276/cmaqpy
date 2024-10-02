"""
This example shows how to run the CCTM benchmark case using the `CMAQModel` class.

You should run this inside a tmux window because this ties up the terminal.

NOTE: Check MCIP input file names $YYYY$MM$DD or $YY$MM$DD in the run script.
"""

from cmaqpy.runcmaq import CMAQModel

# Specify the start/end times
start_datetime = "2018-07-02"  # first day that you want run
end_datetime = "2018-07-09"  # DAY AFTER the last day you want run

# Specify if you want to run the 12 km or the 4 km domain
appl = "2032_12US1_nygrid"

# Define the coordinate name (must match that in GRIDDESC)
if "2032_12US1_nygrid" in appl:
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
    new_mcip=False,
    new_bcon=False,
    new_icon=False,
    verbose=True,
)

# Call the "run_combine" method
cmaq_sim.run_combine(run_hours=2, mem_per_node=20, combine_vrsn="v54", setup_only=True)
