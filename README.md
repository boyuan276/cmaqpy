This repository holds python code to help facilitate running and processing CMAQ simulations.

Instructions for running two scenarios (a base case and a with renewables scenario) for the DEC's 12OTC2 domain (12 km spatial resolution) and 4OTC2 domain (4 km spatial resolution) are included in this README.

*NOTE*: I'm not sure if this package allows you to run multiple instances of CMAQModel simultaneously. 

## Run a new simulation on the 12-km domain
### SMOKE
If you want to run a new simulation, start by preparing your `data/dirpaths_{self.appl}.yml` with directory and file paths. Then, edit the `examples/ex_run_onetime.py` script. To make it easy on yourself, I suggest opening your `NEI_HOME` directory in a separate VSCode window, so you can quickly navigate around the `intermed`, `reports`, and `smoke_out` directories.  

1. Prepare the `{ertac_case}__fs_ff10_future.csv` and the `{ertac_case}_fs_ff10_hourly_future.csv`. Note that you might have to delete comments associated with Tri-Center Naniwa Energy.  
2. Change `appl`. The available options are commented out in the example script.    
3. Change `ertac_case`. The only options that I have developed thus far are `CONUS2016_Base` (the base case) and `CONUS2016_S0` (the with renewables case).    
4. Run `ex_ptertac_onetime.py`. This step should take about 3 hours to run and creates the grid-specific `stack_groups_ptertac` file.     

Then, edit the `examples/ex_ptertac_daily.py` script

1. Change `start_datetime`.   
2. Change `end_datetime`. 
1. Change `appl`  
2. Change `ertac_case`  
3. Run `ex_ptertac_daily.py`. This step should take about 45 minutes to run and creates a grid-specific `inln_mole_ptertac` for each day in the month. NEI designed it's scripts to easily process the full year, so it's easiest to process data in monthly incriments. 
4. If this is not the base case, I manually rename the `smoke_out` directory to append the scenario (e.g., `ptertac_s0`). Yes, I know, there must be a better way of doing this...  

To visualize the point source emissions, you must transfer these files to the CMAQ grid by running `runsmoke.run_inlineto2d`. Note that you must run this fucntion separately for each day that you would like processed.

### CCTM
Finally, edit `examples/ex_run_cctm.py`

1. If not rerunning MCIP, specify the location of your MCIP files using the `LOC_MCIP` variable in `data/dirpaths_{self.appl}.yml`  
2. If not rerunning MCIP, set `new_mcip=False` in your `CMAQModel` instance  
3. Specify the location of your initial and boundary conditions using the `LOC_IC` and `LOC_BC` variables in `data/dirpaths_{self.appl}.yml`
4. Specify the location of your ptertac in-line emissiions files using the `LOC_ERTAC` variable in `data/dirpaths_{self.appl}.yml`
5. Change `start_datetime`.   
6. Change `end_datetime`.    
7. Change `appl`.
8. Run `examples/ex_run_cctm.py` inside a tmux window. This domain takes about 1h 45m per day to run on the 48 proc node on Magma.


### Combine
In order to visualize the data CCTM data properly, you need to postprocess the data using the CMAQ `combine` utility program, which you can run by editing `examples/ex_run_scombine.py`.  
1. Change `start_datetime`.   
2. Change `end_datetime`.   
3. Change `appl`.   
4. Run `examples/ex_run_combine.py`. No need for a tmux window, and this should take several minutes per day of simulaiton time with the default calcualtions. 

## Run a new simulation on the 4-km domian
### SMOKE
If you want to run the 4-km domain after running a simulation on the 12-km domain, many of the steps remain the same. Start by preparing your `data/dirpaths_{self.appl}.yml` with directory and file paths. Then, edit the `examples/ex_ptertac_onetime.py` script.  

1. Change `appl`. The available options are commented out in the example script.  
2. Change `ertac_case`. The only options that I have developed thus far are `CONUS2016_Base` (the base case) and `CONUS2016_S0` (the with renewables case).  
3. Run `ex_ptertac_onetime.py`. This step should take about 2 hours to run, and creates the grid-specific `stack_groups_ptertac*` file. No need for a tmux window.   

Next, edit the `examples/ex_run_daily.py` script.

1. Change `appl`. The available options are commented out in the example script.  
2. Change `ertac_case`  
3. Run `ex_run_daily.py`. This step should take about an hour to run and creates a grid-specific `inln_mole_ptertac` for each day in the month. No need for a tmux window. 
4. If this is not the base case, I manually rename the `smoke_out` directory to append the scenario (e.g., `ptertac_s0`).  

### MCIP
If you need to run MCIP, edit the `examples/ex_run_mcip.py` script  

1. Change `start_datetime`.   
2. Change `end_datetime`. 
1. Change `appl`. The available options are commented out in the example script.
2. Make sure that the start and end dates are correct.
3. Run `examples/ex_run_mcip.py`. Each day takes just over a minute to run on Magma.

### ICON
If you need to run ICON, which you probably don't, edit the `examples/ex_run_icon.py` script. 

1. Change `start_datetime`.   
2. Change `end_datetime`. 
3. Change `appl`. The available options are commented out in the example script.
4. Make sure that the start and end dates are correct. 
5. Check the `coarse_grid_appl`.  
6. Run `examples/ex_run_icon.py`.    

*NOTE*: I'm just using the simulations transferred to us from NYDEC as boundary conditions (CGRID files), so I just simply change the `LOC_IC` variable in `data/dirpaths_{self.appl}.yml` rather than running ICON. 

### BCON
If you need to run BCON, which you probably do, edit the `examples/ex_run_bcon.py` script

1. Change `start_datetime`.   
2. Change `end_datetime`. 
3. Change `appl`. The available options are commented out in the example script.
4. Make sure that the start and end dates are correct. 
5. Check the `coarse_grid_appl`.  
6. Run `examples/ex_run_bcon.py` inside a tmux window. BCON takes about a minute per day to run on Magma.    

### CCTM
Finally, edit `examples/ex_run_cctm.py`

1. If not running MCIP, specify the location of your MCIP files using the `LOC_MCIP` variable in `data/dirpaths_{self.appl}.yml` and set `new_mcip=False` in your `CMAQModel` instance.  
2. If not running BCON, specify the location of you BCON files using the `LOC_BC` variable in `data/dirpaths_{self.appl}.yml` and set `new_bcon=False` in your `CMAQModel` instance.
3. Specify the name of your ptertac in-line emissiions files in the `LOC_ERTAC` variable in `data/dirpaths_{self.appl}.yml`.  
4. Change `start_datetime`.   
5. Change `end_datetime`.  
6. Change `appl`. The available options are commented out in the example script.
7. Run `examples/ex_run_cctm.py` inside a tmux window. This domain takes about 55 min per day to run on the 48 proc node on Magma.

### Combine
In order to visualize the data CCTM data properly, you need to postprocess the data using the CMAQ `combine` utility program, which you can run by editing `examples/ex_run_scombine.py`.  
1. Change `start_datetime`.   
2. Change `end_datetime`.   
3. Change `appl`.   
4. Run `examples/ex_run_combine.py`. No need for a tmux window, and this should take several minutes per day of simulaiton time with the default calcualtions. 
