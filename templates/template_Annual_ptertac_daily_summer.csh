#!/bin/csh -f
#SBATCH -J ptertac_summer		# Job name
%SLURM%
#SBATCH -o /mnt/data1/by276/emissions_data/nei_platform2016/v1/2016fh_16j/intermed/ptertac/logs/out_ptertac_summer.%j		# Name of stdout output file (%j expands to jobId) 

limit stacksize unlimited
limit memoryuse unlimited

setenv SECTOR "ptertac"

if ($?SLURM_SUBMIT_DIR) then
  cd $SLURM_SUBMIT_DIR
endif

## Definitions for case name, directory structures, etc, that are used
#  by every sector in the case
#  Anything defined in directory_definitions can be overridden here 
#  if desired
%DIR_DEF%

## Months for emissions processing, and spinup duration
#  In the EPA emissions modeling platforms, the only sectors that use
#    SPINUP_DURATION are biogenics and the final sector merge (Mrggrid).
#  Elsewhere, SPINUP_DURATION = 0, and when Mrggrid runs for spinup days,
#    base year emissions are used for the spinup year for all sectors except
#    biogenics.
#  Effective Jan 2019, SPINUP_DURATION now should work for all months.
#  SPINUP_MONTH_END (new for Jan 2019) specifies whether the last $SPINUP_DURATION 
#    days of quarter 2/3/4 should be run at the end of a quarter (Y), or at the start 
#    of the next quarter (N). For example, if runningwith SPINUP_DURATION = 10:
#    When N (old behavior), Q1 will include 10 day spinup and end on 3/21; Q2 will
#    cover 3/22 through 6/20. When Y, Q1 will include 10 day spinup and end on 3/31
#    (including all of March), remaining quarters will function as if spinup = 0.
#
# setenv RUN_MONTHS "5 6 7 8 9" #summer
setenv RUN_MONTHS " 8 " #summer
setenv SPINUP_DURATION "0"
setenv SPINUP_MONTH_END "Y"

## Emissions modeling year
#  (i.e. meteorological year, not necessarily the inventory year"
setenv BASE_YEAR "2016"
setenv EPI_STDATE_TIME "${BASE_YEAR}-01-01 00:00:00.0"
setenv EPI_ENDATE_TIME "${BASE_YEAR}-12-31 23:59:00.0"

## Inventory case name, if inventories are coming from a different case (they usually aren't)
#  CASEINPUTS is defined in directory_definitions and optionally overridden here
#setenv INVENTORY_CASE "2011ek_cb6v2_v6_11g"
#setenv CASEINPUTS "$INSTALL_DIR/$INVENTORY_CASE/inputs"

## Inputs for all sectors
setenv AGREF "${GE_DAT}/gridding/agref_us_2014platform_21aug2019_nf_v17.txt"
setenv ARTOPNT "${GE_DAT}/artopnt_2002detroit_20aug2019_v2.txt"
setenv ATPRO_HOURLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_hourly_6nov2014_24jul2017_v5"
setenv ATPRO_HOURLY_NCF "${GE_DAT}/temporal/Gentpro_TPRO_HOUR_HOURLY_BASH_NH3.agNH3_bash_2016j_12US2_smk37.ncf"
setenv ATPRO_MONTHLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_monthly_6nov2014_30nov2018_nf_v9"
setenv ATPRO_WEEKLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_weekly_6nov2014_09sep2016_v2"
setenv ATREF "${GE_DAT}/temporal/amptref_general_2014platform_tref_21aug2019_nf_v17"
setenv COSTCY "${GE_DAT}/costcy_2016v1_platform_30jan2019_v0.txt"
setenv EFTABLES "$CASEINPUTS/onroad/eftables/rateperdistance_smoke_aq_cb6_saprc_1Aug2019_2016v1platform-2016-20190718_10003_1.csv"
%GRID%
setenv GSCNV "${GE_DAT}/speciation/spec_parts/gscnv_Create_Speciate4_5_CB6CMAQ_04jan2018_nf_v1.txt"
setenv GSPROTMP_A "${GE_DAT}/speciation/2016fh_16j/gspro_cmaq_cb6_2016fh_16j_nf.txt"
setenv GSREFTMP_A "${GE_DAT}/speciation/2016fh_16j/gsref_cmaq_cb6_2016fh_16j_nf.txt"
setenv HOLIDAYS "${GE_DAT}/temporal/holidays_13feb2017_v1.txt"
#setenv INVTABLE "${GE_DAT}/invtable_2014platform_integrate_21dec2018_v3.txt"
setenv MRGDATE_FILES "$INSTALL_DIR/smoke4.7/scripts/smk_dates/2016/smk_merge_dates_201601.txt"
setenv MTPRO_HOURLY "${GE_DAT}/temporal/mtpro_hourly_MOVES_2014v2_03nov2017_v0"
setenv MTPRO_MONTHLY "${GE_DAT}/temporal/mtpro_monthly_MOVES_03aug2016_v1"
setenv MTPRO_WEEKLY "${GE_DAT}/temporal/mtpro_weekly_MOVES_2014v2_03nov2017_v0"
setenv MTREF "${GE_DAT}/temporal/mtref_onroad_MOVES_2014v2_19sep2018_nf_v2"
setenv NAICSDESC "${GE_DAT}/smkreport/naicsdesc_02jan2008_v0.txt"
setenv ORISDESC "${GE_DAT}/smkreport/orisdesc_04dec2006_v0.txt"
#setenv PELVCONFIG "${GE_DAT}/point/pelvconfig_inline_20m_13nov2012_v0.txt"
setenv PSTK "${GE_DAT}/point/pstk_13nov2018_v1.txt"
#setenv PTPRO_HOURLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_hourly_6nov2014_24jul2017_v5"
#setenv PTPRO_MONTHLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_monthly_6nov2014_30nov2018_nf_v9"
setenv PTPRO_WEEKLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_weekly_6nov2014_09sep2016_v2"
#setenv PTREF "${GE_DAT}/temporal/amptref_general_2014platform_tref_21aug2019_nf_v17"
#setenv REPCONFIG_GRID "${GE_DAT}/smkreport/repconfig/repconfig_area_inv_grid_2016beta_07feb2019_v0.txt"
#setenv REPCONFIG_INV "${GE_DAT}/smkreport/repconfig/repconfig_area_inv_2016beta_07feb2019_v0.txt"
setenv SCCDESC "${GE_DAT}/smkreport/sccdesc_2014platform_21aug2019_nf_v3.txt"
setenv SECTORLIST "$CASESCRIPTS/sectorlist_2016fh_02aug2019_v0"
setenv SRGDESC "${GE_DAT}/gridding/srgdesc_CONUS12_2014_v1_3_29nov2016_10jul2019_nf_v4.txt"
setenv SRGPRO "${GE_DAT}/gridding/surrogates/CONUS12_2014_30apr2019/USA_100_NOFILL.txt"
setenv XPORTFRAC "${GE_DAT}/gridding/xportfrac.12US1.GRIDCRO2D.ncf"

# Inputs specific to this sector
setenv INVTABLE "${GE_DAT}/invtable_2014platform_nointegrate_07dec2018_v1.txt"
setenv PELVCONFIG "${GE_DAT}/point/pelvconfig_seca_c3_22jul2010_v1.txt"
setenv REPCONFIG_INV "${GE_DAT}/smkreport/repconfig/repconfig_point_inv_2016beta_07feb2019_v0.txt"
setenv REPCONFIG_TEMP "${GE_DAT}/smkreport/repconfig/repconfig_point_temporal_2016beta_07feb2019_v0.txt"
%EMIS%

setenv GSPRO_COMBO "${GE_DAT}/speciation/gspro_combo_2010cdc_2010ef_nonpt_12nov2012_v0.txt"
setenv REPCONFIG_GRID "${GE_DAT}/smkreport/repconfig/repconfig_point_invgrid_2011platform_11aug2014_v0.txt"
setenv CEMSUM "${GE_DAT}/point/cemsum_2016v1_3_14_2018.txt"
setenv PTPRO_WEEKLY "${GE_DAT}/temporal/noncem_2016beta_tpro_weekly_30nov2018_v0"
setenv PTPRO_MONTHLY "${GE_DAT}/temporal/noncem_2016beta_tpro_monthly_02jan2019_v1"
setenv PTPRO_DAILY "${GE_DAT}/temporal/noncem_2016beta_tpro_daily_30nov2018_v0"
setenv REPCONFIG_INV3 "${GE_DAT}/smkreport/repconfig/repconfig_point_inv_vocprof_2016beta_07feb2019_v0.txt"

# Parameters for all sectors
setenv FILL_ANNUAL "N"
#setenv FULLSCC_ONLY "Y"
#setenv INLINE_MODE "both"
setenv IOAPI_ISPH "20"
#setenv L_TYPE "mwdss"
#setenv M_TYPE "mwdss"
setenv MRG_MARKETPEN_YN "N"
setenv MRG_REPCNY_YN "Y"
setenv MRG_REPSTA_YN "N"
setenv MTMP_OUTPUT_YN "N"
setenv NO_SPC_ZERO_EMIS "Y"
setenv OUTPUT_FORMAT "$EMF_AQM"
setenv OUTZONE "0"
setenv PLATFORM "v7.3"
setenv POLLUTANT_CONVERSION "Y"
setenv RAW_DUP_CHECK "N"
setenv RENORM_TPROF "Y"
setenv REPORT_DEFAULTS "Y"
setenv RUN_HOLIDAYS "Y"
setenv RUN_PYTHON_ANNUAL "Y"
setenv SMK_AVEDAY_YN "N"
setenv SMK_DEFAULT_SRGID "100"
setenv SMKINVEN_FORMULA "PMC=PM10-PM2_5"
setenv SMK_MAXERROR "10000"
setenv SMK_MAXWARNING "10"
setenv SMKMERGE_CUSTOM_OUTPUT "Y"
setenv SMK_PING_METHOD "0"
setenv SMK_SPECELEV_YN "Y"
setenv SPC "$EMF_SPC"
setenv SPINUP_MONTH_END "Y"
setenv WEST_HSPHERE "Y"

# Sector-specific parameters
setenv WRITE_ANN_ZERO "Y"
setenv L_TYPE "all"
setenv M_TYPE "all"
setenv DAY_SPECIFIC_YN "N"
setenv HOUR_SPECIFIC_YN "Y"
setenv NAMEBREAK_HOURLY "4"
setenv INLINE_MODE "only"
setenv ZIPOUT "Y"
setenv SORT_LIST_EVS "Y"
setenv USE_FF10_DAILY_POINT "N"
setenv USE_FF10_HOURLY_POINT "Y"

# Inputs for summer only
setenv PTREF "${GE_DAT}/temporal/noncem_2016beta_tref_summer_23jul2019_v4"
setenv PTPRO_HOURLY "${GE_DAT}/temporal/noncem_2016beta_tpro_hourly_summer_30nov2018_v0"
setenv FULLSCC_ONLY "N"

# Inputs for winter only
#setenv PTREF "${GE_DAT}/temporal/noncem_2016beta_tref_winter_23jul2019_v4"
#setenv PTPRO_HOURLY "${GE_DAT}/temporal/noncem_2016beta_tpro_hourly_winter_30nov2018_v0"
#setenv FULLSCC_ONLY "N"

$RUNSCRIPTS/emf/smk_pt_daily_emf.csh $REGION_ABBREV $REGION_IOAPI_GRIDNAME -m "$RUN_MONTHS" $SPINUP_DURATION winter
