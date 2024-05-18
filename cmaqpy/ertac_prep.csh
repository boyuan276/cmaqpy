#!/bin/tcsh

#SBATCH -J ertac_prep		# Job name
#SBATCH -o /home/jas983/models/ertac_egu/ertac_prep_%j.log		# Name of stdout output file (%j expands to jobId)
#SBATCH --nodes=1		# Total number of nodes requested 
#SBATCH --ntasks=1		# Total number of tasks to be configured for. 
#SBATCH --tasks-per-node=1	# sets number of tasks to run on each node. 
#SBATCH --cpus-per-task=1	# sets number of cpus needed by each task (if task is "make -j3" number should be 3).
#SBATCH --get-user-env		# tells sbatch to retrieve the users login environment. 
#SBATCH -t 30:00:00		# Run time (hh:mm:ss)
#SBATCH --mem=20000M		# memory required per node 
#SBATCH --partition=default_cpu	# Which queue it should run on.

setenv CASENOUS CONUS2016_Base
setenv CASE ${CASENOUS}_

## Delete the case directory if it already exists
rm -r /home/jas983/models/ertac_egu/${CASENOUS}

## Create a new directory for the case based upon the template
cp -r /home/jas983/models/ertac_egu/CONUS2016_template /home/jas983/models/ertac_egu/${CASENOUS}

## Change into this new case directory
cd /home/jas983/models/ertac_egu/${CASENOUS}

## Link the input files
ln -s inputs/ertac_control_emissions.csv ertac_control_emissions.csv
ln -s inputs/ertac_growth_rates.csv ertac_growth_rates.csv
ln -s inputs/ertac_initial_uaf_v2.csv ertac_initial_uaf_v2.csv
ln -s inputs/ertac_input_variables_v2.csv ertac_input_variables_v2.csv
ln -s inputs/ertac_hourly_noncamd.csv ertac_hourly_noncamd.csv
ln -s inputs/camd_hourly_base.csv camd_hourly_base.csv
##ln -s inputs/ertac_demand_transfer.csv ertac_demand_transfer.csv
##ln -s inputs/ertac_seasonal_control_emissions.csv ertac_seasonal_control_emissions.csv
##ln -s inputs/group_total_listing.csv group_total_listing.csv
##ln -s inputs/state_total_listing.csv state_total_listing.csv

## Run the preprocessing step
/usr/bin/python /home/jas983/models/ertac_egu/ertac_v2.1.1/ertac_preprocess.py -o ${CASE}

mkdir outputs
mv ${CASE}* outputs/

exit;
