#!/bin/csh

# This script defines case names, directory structures and locations,
#   and defines other environment variables that are used by all sectors
#   and should not need to be changed on a sector-by-sector basis.
# All sector scripts call this "assigns" script at the very top.

# Eventually, this script will also check that some or all SMOKE inputs
#   are actually in the directories as defined by this script. 
#   This functionality is a future feature.

%DIR%

# Location of full layered METCRO3D files if different than MET_ROOT directory; 
# These are only needed if running fires with 3-D plume rise for CAMx modeling;
#   you may be able to set this equal to $MET_ROOT
setenv MET_ROOT_3D $MET_ROOT 
if ($SECTOR == ptfire3D || $SECTOR == ptfire_othna3D || $SECTOR == ptagfire3D) setenv MET_ROOT $MET_ROOT_3D

%CASE%

## SMOKE version - leave this alone, even if not using SMOKE 4.7
## SMOKE 4.7 or newer is required for this emissions platform, but
#  if not using SMOKE 4.7, use SMOKE_LOCATION parameter above 
#  to define the location of the SMOKE executables; do not change
#  MODEL_LABEL because this is also used to reference the run scripts
#  in some helper scripts
setenv MODEL_LABEL "SMOKE4.7"

## Defines the SMOKE input/output directory structure
setenv PROJECT "$CASE"
setenv OUT_ROOT "$INSTALL_DIR"
setenv PROJECT_ROOT "$INSTALL_DIR"
setenv IMD_ROOT "$PROJECT_ROOT/$CASE/intermed"
setenv DAT_ROOT $PROJECT_ROOT
setenv SMK_HOME "$INSTALL_DIR"
setenv CASEINPUTS "$INSTALL_DIR/$CASE/inputs"
setenv GE_DAT "$INSTALL_DIR/ge_dat"
setenv CASESCRIPTS "$PROJECT_ROOT/$CASE/scripts"
setenv RUNSCRIPTS "$INSTALL_DIR/smoke4.7/scripts"
setenv RUNSET "$CASESCRIPTS/run_settings.txt"
setenv ASSIGNS_FILE "$INSTALL_DIR/smoke4.7/assigns/ASSIGNS.emf"

## On EPA systems, run scripts interface with the Emissions Modeling Framework (EMF).
#  Setting EMF_CLIENT to "false" is the easiest way to disable this interaction, 
#  allowing these scripts to run on other systems
setenv EMF_CLIENT false

## Other variables related to the EMF; these are not used by SMOKE 
#  but may be required by the scripts to at least exist; leave these alone
setenv EMF_AQM "CMAQ v5.2"
setenv EMF_JOBNAME "Annual_area"
setenv EMF_SCRIPTDIR "${CASESCRIPTS}"
setenv EMF_SCRIPTNAME "${CASESCRIPTS}/${EMF_JOBNAME}.csh"
setenv EMF_LOGNAME "${CASESCRIPTS}/logs/$EMF_SCRIPTNAME.log"
setenv EMF_JOBKEY "28310_1312400444602"
setenv EMF_QUEUE_OPTIONS_C "--mem-per-cpu=20g -n 1 -p compute -A emis --gid=emis-hpc -t 168:00:00"
setenv EMF_LOGGERPYTHONDIR "$EMF_SCRIPTDIR/case_logs_python"
setenv EMF_JOBID "1"
