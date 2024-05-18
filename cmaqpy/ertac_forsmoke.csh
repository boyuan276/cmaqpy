#!/bin/tcsh

#SBATCH -J ertac_fs		# Job name
#SBATCH -o /home/jas983/models/ertac_egu/CONUS2016_Base/ertac_fs_%j.log		# Name of stdout output file (%j expands to jobId)
#SBATCH --nodes=1		# Total number of nodes requested 
#SBATCH --ntasks=1		# Total number of tasks to be configured for. 
#SBATCH --tasks-per-node=1	# sets number of tasks to run on each node. 
#SBATCH --cpus-per-task=1	# sets number of cpus needed by each task (if task is "make -j3" number should be 3).
#SBATCH --get-user-env		# tells sbatch to retrieve the users login environment. 
#SBATCH -t 60:00:00		# Run time (hh:mm:ss) 
#SBATCH --mem=20000M		# memory required per node
#SBATCH --partition=default_cpu	# Which queue it should run on. 

setenv CASENOUS CONUS2016_Base
setenv CASE ${CASENOUS}_

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

## Run the projection step
/usr/bin/python /home/jas983/models/ertac_egu/ertac_v2.1.1/ertac_projection.py -i outputs/${CASE} -o ${CASE}p_ 

mv ${CASE}p_* outputs

## Run the postprocess step
/usr/bin/python /home/jas983/models/ertac_egu/ertac_v2.1.1/ertac_postprocess.py --input-prefix-pre=outputs/${CASE} --input-prefix-proj=outputs/${CASE}p_  --output-prefix=${CASE} --include-st-hr --include-rg-hr --include-unit-day

cp ${CASE}post_results/annual_unit_summary.csv outputs/${CASE}annual_unit_level_summary.csv
mv ${CASE}ertac_egu_postprocessing_log.txt outputs/${CASE}ertac_egu_postprocessing_log.txt

## Run the ertac for smoke conversion tool 
/usr/bin/python /home/jas983/models/ertac_egu/ertac_v2.1.1/ertac_for_smoke.py --input-prefix-pre=outputs/${CASE} --input-prefix-proj=outputs/${CASE}p_ --input-prefix-fs=ERTAC_for_SMOKE_extra_inputs/FS_CONUSv16.0_2023_181002_ --input-prefix-pp=${CASE}post_results/ -o ${CASE}fs_

## Clean up outputs
mkdir for_SMOKE

mv ${CASE}fs* for_SMOKE/
cp ${CASE}post_results/annual_summary_with_other_pollutants.csv outputs/${CASE}annual_summary_with_other_pollutants.csv
cp ${CASE}post_results/annual_summary_with_other_pollutants.csv for_SMOKE/${CASE}annual_summary_with_other_pollutants.csv
cp for_SMOKE/${CASE}fs_ertac_egu_for_smoke_log.txt outputs/${CASE}fs_ertac_egu_for_smoke_log.txt

exit;
