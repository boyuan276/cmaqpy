import datetime
import os
import sys
import time
from . import utils
from .data.fetch_data import fetch_yaml


class CMAQModel:
    """
    This class provides a framework for running the CMAQ Model.

    NOTE: evetnually need to figure out how to link files for representative days 
    through the following Sunday. Right now, I do this manually by adding 1 to the 
    length of days. 

    Parameters
    ----------
    :param start_datetime: string
        Start date for the CMAQ simulation. I think you can technically 
        start CMAQ at any time, but it's probably best to simply start at 00:00 UTC. 
    :param end_datetime: string
        Date after the last day for which you want to run CMAQ. E.g., if you list
        August 4, 2016 the simulation will end August 4, 2016 00:00 UTC.
    :param appl: string
        Application name. Used primarily for directory and file naming.
    :param coord_name: string
        Coordinate name which must match the GRIDDESC file (e.g., LAM_40N100W).
    :param grid_name: string
        Grid name which must match the GRIDDESC file (e.g., 12OTC2).
    :param chem_mech: string
        CMAQ chemical mechanism. This defaults to "cb6r3_ae7_aq."
    :param cctm_vrsn: string
        Version identifier for CCTM, which is required for identifying the
        executables.
    :param setup_yaml: string
        Name of the yaml file containin your directory paths if located in this directory.
        Otherwise, use the full file path. 
    :param compiler: string
        Compiler identifier for use in naming.
    :param compiler_vrsn: string
        Compiler version number for use in naming. 
    :param new_mcip: bool
        Option to run MCIP or use MCIP output from a previous run. Defaults to True. 
    :param new_icon: bool
        Option to run ICON or use ICON output (or a CGRID file) from a previous run.
        Defualts to False.
    :param icon_vrsn: string
        ICON version number for use in naming.
    :param icon_type: string
        Method for creating initial conditions. Options are [profile, regrid].
    :param new_bcon: bool
        Option to run BCON or use BCON output from a previous run. Defaults to True.
    :param bcon_vrsn: string
        BCON version number for use in naming. 
    :param bcon_type: string 
        Method for creating boundary conditions. Options are [profile, regrid].
    :param verbose: bool
        When True, additional information is prited to the screen about simulation progress.

    See also
    --------
    SMOKEModel: setup and run the SMOKE model. 
    """
    def __init__(self, start_datetime, end_datetime, appl, coord_name, grid_name, 
                 chem_mech='cb6r3_ae7_aq', cctm_vrsn='v533', setup_yaml='dirpaths.yml', 
                 compiler='gcc', compiler_vrsn='9.3.1', new_mcip=True, new_icon=False, 
                 icon_vrsn='v532', icon_type='regrid', new_bcon=True, bcon_vrsn='v532', 
                 bcon_type='regrid', verbose=False):
        self.appl = appl
        self.coord_name = coord_name
        self.grid_name = grid_name
        self.chem_mech = chem_mech
        self.cctm_vrsn = cctm_vrsn
        self.compiler = compiler
        self.compiler_vrsn = compiler_vrsn
        self.new_icon = new_icon
        self.icon_vrsn = icon_vrsn
        self.icon_type = icon_type
        self.new_bcon = new_bcon
        self.bcon_vrsn = bcon_vrsn
        self.bcon_type = bcon_type
        self.verbose = verbose
        self.cctm_runid = f'{self.cctm_vrsn}_{self.compiler}{self.compiler_vrsn}_{self.appl}'
        if self.verbose:
            print(f'Application name: {self.appl}\nCoordinate name: {self.coord_name}\nGrid name: {self.grid_name}')
            print(f'CCTM RUNID: {self.cctm_runid}')

        # Format the forecast start/end and determine the total time.
        self.start_datetime = utils.format_date(start_datetime)
        self.end_datetime = utils.format_date(end_datetime)
        self.delt = self.end_datetime - self.start_datetime
        if self.verbose:
            print(f'CMAQ run starting on: {self.start_datetime}')
            print(f'CMAQ run ending on: {self.end_datetime}')

        # Define the domain windowing paramters for MCIP. 
        # Could perhaps move this to the run_mcip method.
        if self.grid_name == '12OTC2':
            self.mcip_btrim = -1
            self.mcip_x0 = 141
            self.mcip_y0 = 15
            self.mcip_ncols = 273
            self.mcip_nrows = 246  
        elif self.grid_name == '4OTC2':
            self.mcip_btrim = -1
            self.mcip_x0 = 87
            self.mcip_y0 = 9
            self.mcip_ncols = 126
            self.mcip_nrows = 156
        else:
            # This will use the entire WRF domain
            self.mcip_btrim = 0
            self.mcip_x0 = 0
            self.mcip_y0 = 0
            self.mcip_ncols = 0
            self.mcip_nrows = 0

        # Set working and WRF model directory names
        dirs = fetch_yaml(setup_yaml)
        self.dirpaths = dirs.get('directory_paths')
        self.filepaths = dirs.get('file_paths')
        self.filenames = dirs.get('file_names')
        self.CMAQ_HOME = self.dirpaths.get('CMAQ_HOME')
        self.MCIP_SCRIPTS = f'{self.CMAQ_HOME}/PREP/mcip/scripts'
        self.ICON_SCRIPTS = f'{self.CMAQ_HOME}/PREP/icon/scripts'
        self.BCON_SCRIPTS = f'{self.CMAQ_HOME}/PREP/bcon/scripts'
        self.CCTM_SCRIPTS = f'{self.CMAQ_HOME}/CCTM/scripts'
        self.COMBINE_SCRIPTS = f'{self.CMAQ_HOME}/POST/combine/scripts'
        self.CMAQ_DATA = self.dirpaths.get('CMAQ_DATA')
        if new_mcip:
            self.MCIP_OUT = f'{self.CMAQ_DATA}/{self.appl}/mcip'
        else:
            self.MCIP_OUT = self.dirpaths.get('LOC_MCIP')
        self.CCTM_INPDIR = f'{self.CMAQ_DATA}/{self.appl}/input'
        self.CCTM_OUTDIR = f'{self.CMAQ_DATA}/{self.appl}/output_CCTM_{self.cctm_runid}'
        self.ICBC = f'{self.CCTM_INPDIR}/icbc'
        self.CCTM_GRIDDED = f'{self.CCTM_INPDIR}/emis/gridded_area'
        # self.CCTM_RWC = f'{self.CCTM_INPDIR}/emis/gridded_area/rwc'
        # self.CCTM_BEIS = f'{self.CCTM_INPDIR}/emis/gridded_area/beis'
        self.CCTM_PT = f'{self.CCTM_INPDIR}/emis/inln_point'
        self.CCTM_LAND = f'{self.CCTM_INPDIR}/land'
        self.POST = f'{self.CMAQ_DATA}/{self.appl}/post'
        if new_icon:
            self.LOC_IC = self.CCTM_OUTDIR
        else:
            self.LOC_IC = self.dirpaths.get('LOC_IC')
        if new_bcon:
            self.LOC_BC = f'{self.CMAQ_DATA}/{self.appl}/bcon'
        else:
            self.LOC_BC = self.dirpaths.get('LOC_BC')
        self.LOC_GRIDDED_AREA = self.dirpaths.get('LOC_GRIDDED_AREA')
        self.LOC_RWC = self.dirpaths.get('LOC_RWC')
        self.LOC_BEIS = self.dirpaths.get('LOC_BEIS')
        self.LOC_IN_PT = self.dirpaths.get('LOC_IN_PT')
        self.LOC_ERTAC = self.dirpaths.get('LOC_ERTAC')
        self.LOC_SMK_MERGE_DATES = self.dirpaths.get('LOC_SMK_MERGE_DATES')
        self.LOC_LAND = self.dirpaths.get('LOC_LAND')
        self.DIR_TEMPLATES = self.dirpaths.get('DIR_TEMPLATES')
        self.InMetDir = self.dirpaths.get('InMetDir')
        self.InGeoDir = self.dirpaths.get('InGeoDir')

        # Define the locations for CMAQ inputs
        self.GRIDDESC = self.filepaths.get('GRIDDESC')
        self.SECTORLIST = self.filepaths.get('SECTORLIST')

        # Define the names of the CMAQ output files
        #### Maybe use this in the future ####

        # Define linux command aliases
        self.CMD_LN = 'ln -sf %s %s'
        self.CMD_CP = 'cp %s %s'
        self.CMD_MV = 'mv %s %s'
        self.CMD_RM = 'rm %s'
        self.CMD_GUNZIP = 'gunzip %s'

    def run_mcip(self, mcip_start_datetime=None, mcip_end_datetime=None, metfile_list=[], 
                 geo_file='geo_em.d01.nc', t_step=60, run_hours=4, setup_only=False):
        """
        Setup and run MCIP, which formats meteorological files (e.g. wrfout*.nc) for CMAQ.

        Parameters
        ----------
        :param mcip_start_datetime: string
            Start date and time for MCIP. Defaults to None in which case the MCIP start 
            datetime will be assigned from the CMAQ start datetime. 
        :param mcip_end_datetime: string
            End date and time for MCIP. Defaults to None in which case the MCIP end 
            datetime will be assigned from the CMAQ end datetime.
        :param metfile_list: list
            List of wrfout* files, which must be located in `self.InMetDir`, that will
            be processed by MCIP.
        :param geo_file: string
            Name of geo_em* file associated with the wrfout* files you are processing.
        :param t_step: int
            Time step (MCIP INTVL parameter) of output data in minutes. Defaults to 60 
            min (1 hour).
        :param run_hours: int
            Number of hours to request from the scheduler.
        :setup_only: bool
            Option to setup the directories and write the scripts without running MCIP.
        """
        ## SETUP MCIP
        if mcip_start_datetime is None:
            mcip_start_datetime = self.start_datetime
        else:
            mcip_start_datetime = utils.format_date(mcip_start_datetime)
        if mcip_end_datetime is None:
            mcip_end_datetime = self.end_datetime
        else:
            mcip_end_datetime = utils.format_date(mcip_end_datetime)
        # Set an 'MCIP APPL,' which will control file names
        mcip_sdatestr = mcip_start_datetime.strftime("%y%m%d")
        self.mcip_appl = f'{self.appl}_{mcip_sdatestr}'
        # Remove existing log file
        cmd = self.CMD_RM % (f'{self.MCIP_SCRIPTS}/run_mcip_{self.mcip_appl}.log')
        os.system(cmd)
        
        # Copy the template MCIP run script to the scripts directory
        run_mcip_path = f'{self.MCIP_SCRIPTS}/run_mcip_{self.mcip_appl}.csh'
        cmd = self.CMD_CP % (f'{self.DIR_TEMPLATES}/template_run_mcip.csh', run_mcip_path)
        os.system(cmd)

        # Write Slurm info
        mcip_slurm =  f'#SBATCH -J mcip_{self.appl}		# Job name\n'
        mcip_slurm += f'#SBATCH -o {self.MCIP_SCRIPTS}/run_mcip_{self.mcip_appl}.log\n'
        mcip_slurm += f'#SBATCH --nodes=1		# Total number of nodes requested\n' 
        mcip_slurm += f'#SBATCH --ntasks=1		# Total number of tasks to be configured for.\n' 
        mcip_slurm += f'#SBATCH --tasks-per-node=1	# sets number of tasks to run on each node.\n' 
        mcip_slurm += f'#SBATCH --cpus-per-task=1	# sets number of cpus needed by each task.\n'
        mcip_slurm += f'#SBATCH --get-user-env		# tells sbatch to retrieve the users login environment.\n' 
        mcip_slurm += f'#SBATCH -t {run_hours}:00:00		# Run time (hh:mm:ss)\n' 
        mcip_slurm += f'#SBATCH --mem=20000M		# memory required per node\n'
        mcip_slurm += f'#SBATCH --partition=default_cpu	# Which queue it should run on.\n'
        utils.write_to_template(run_mcip_path, mcip_slurm, id='%SLURM%') 

        # Write IO info to the MCIP run script
        mcip_io =  f'source {self.CMAQ_HOME}/config_cmaq.csh {self.compiler} {self.compiler_vrsn}\n'
        mcip_io += f'set APPL       = {mcip_sdatestr}\n'
        mcip_io += f'set CoordName  = {self.coord_name}\n'
        mcip_io += f'set GridName   = {self.grid_name}\n'
        mcip_io += f'set DataPath   = {self.CMAQ_DATA}\n'
        mcip_io += f'set InMetDir   = {self.InMetDir}\n'
        mcip_io += f'set InGeoDir   = {self.InGeoDir}\n'
        mcip_io += f'set OutDir     = {self.MCIP_OUT}\n'
        mcip_io += f'set ProgDir    = $CMAQ_HOME/PREP/mcip/src\n'
        mcip_io += f'set WorkDir    = $OutDir\n'
        utils.write_to_template(run_mcip_path, mcip_io, id='%IO%')

        # Write met info to the MCIP run script
        mcip_met = f'set InMetFiles = ( ' 
        for ii, metfile in enumerate(metfile_list):
            if ii < len(metfile_list) - 1:
                mcip_met += f'$InMetDir/{metfile} \\\n'
            else:
                mcip_met += f'$InMetDir/{metfile} )\n'
        mcip_met += f'set IfGeo      = "T"\n'
        mcip_met += f'set InGeoFile  = {self.InGeoDir}/{geo_file}\n'
        utils.write_to_template(run_mcip_path, mcip_met, id='%MET%')

        # Write start/end info to MCIP run script   
        mcip_time =  f'set MCIP_START = {mcip_start_datetime.strftime("%Y-%m-%d_%H:%M:%S.0000")}\n'  # [UTC]
        mcip_time += f'set MCIP_END   = {mcip_end_datetime.strftime("%Y-%m-%d_%H:%M:%S.0000")}\n'  # [UTC]
        mcip_time += f'set INTVL      = {t_step}\n' # [min]
        utils.write_to_template(run_mcip_path, mcip_time, id='%TIME%')

        # Write domain windowing parameters to MCIP run script
        mcip_domain  = f'set BTRIM = {self.mcip_btrim}\n'
        mcip_domain += f'set X0    =  {self.mcip_x0}\n'
        mcip_domain += f'set Y0    =  {self.mcip_y0}\n'
        mcip_domain += f'set NCOLS =  {self.mcip_ncols}\n'
        mcip_domain += f'set NROWS =  {self.mcip_nrows}\n'
        utils.write_to_template(run_mcip_path, mcip_domain, id='%DOMAIN%')

        if self.verbose:
            print(f'Wrote MCIP run script to\n{run_mcip_path}')

        ## RUN MCIP
        if not setup_only:
            # Begin MCIP simulation clock
            simstart = datetime.datetime.now()
            if self.verbose:
                print('Starting MCIP at: ' + str(simstart))
                # sys.stdout.flush()
            os.system(f'sbatch --requeue {self.MCIP_SCRIPTS}/run_mcip_{self.mcip_appl}.csh')
            # Sleep until the run_mcip_{self.appl}.log file exists
            while not os.path.exists(f'{self.MCIP_SCRIPTS}/run_mcip_{self.mcip_appl}.log'):
                time.sleep(1)
            mcip_sim = self.finish_check('mcip')
            while mcip_sim != 'complete':
                if mcip_sim == 'failed':
                    return False
                else:
                    time.sleep(2)
                    mcip_sim = self.finish_check('mcip')
            elapsed = datetime.datetime.now() - simstart
            if self.verbose:
                print(f'MCIP ran in: {utils.strfdelta(elapsed)}\n')
        return True

    def run_mcip_multiday(self, metfile_dir=None, metfile_list=[], geo_file='geo_em.d01.nc', t_step=60):
        """
        Run MCIP over multiple days. Per CMAQ convention, daily MCIP files contain
        25 hours each all the hours from the current day, and the first hour (00:00)
        from the following day.

        Parameters
        ----------
        :param metfile_dir: string
            Path to the directory where the wrfout* files are located.
        :param metfile_list: list
            List of wrfout* files, located in `metfile_dir`, that will be processed by MCIP.
        :param geo_file: string
            Name of geo_em* file associated with the wrfout* files you are processing.
        :param t_step: int
            Time step (MCIP INTVL parameter) of output data in minutes. Defaults to 60 
            min (1 hour).
        """
        # Loop over each day
        for day_no in range(self.delt.days):
            success = False
            # Set the start datetime, end datetime, and metfile list for the day
            mcip_start_datetime = self.start_datetime + datetime.timedelta(day_no)
            mcip_end_datetime = self.start_datetime + datetime.timedelta(day_no + 1)
            if self.verbose:
                print(f'--> Working on MCIP for {mcip_start_datetime}')
            if metfile_dir is None:
                # If all the met data is stored in the same file, pass that file in 
                # using metfile_list and set metfile_dir=None
                metfile_list = metfile_list
            else:
                # Eventually, can add scripting here that assumes there's a different
                # wrfout file produced every day and they are all located in metfile_dir.
                pass

            # run mcip for that day
            self.run_mcip(mcip_start_datetime=mcip_start_datetime, mcip_end_datetime=mcip_end_datetime, metfile_list=metfile_list, geo_file=geo_file, t_step=t_step, setup_only=False) 
        
    def run_icon(self, coarse_grid_appl='coarse', run_hours=2, setup_only=False):
        """
        Setup and run ICON, which produces initial conditions for CMAQ.

        Parameters
        ----------
        :param coarse_grid_appl: string
            Application name for the coarse grid from which you are deriving initial conditions.
        :param run_hours: int
            Number of hours to request from the scheduler.
        :setup_only: bool
            Option to setup the directories and write the scripts without running ICON.
        """
        ## SETUP ICON
        # Copy the template ICON run script to the scripts directory
        run_icon_path = f'{self.ICON_SCRIPTS}/run_icon.csh'
        cmd = self.CMD_CP % (f'{self.DIR_TEMPLATES}/template_run_icon.csh', run_icon_path)
        os.system(cmd)

        # Write Slurm info
        icon_slurm =  f'#SBATCH -J icon_{self.appl}		# Job name\n'
        icon_slurm += f'#SBATCH -o {self.ICON_SCRIPTS}/run_icon_{self.appl}.log\n'
        icon_slurm += f'#SBATCH --nodes=1		# Total number of nodes requested\n' 
        icon_slurm += f'#SBATCH --ntasks=1		# Total number of tasks to be configured for.\n' 
        icon_slurm += f'#SBATCH --tasks-per-node=1	# sets number of tasks to run on each node.\n' 
        icon_slurm += f'#SBATCH --cpus-per-task=1	# sets number of cpus needed by each task.\n'
        icon_slurm += f'#SBATCH --get-user-env		# tells sbatch to retrieve the users login environment.\n' 
        icon_slurm += f'#SBATCH -t {run_hours}:00:00		# Run time (hh:mm:ss)\n' 
        icon_slurm += f'#SBATCH --mem=20000M		# memory required per node\n'
        icon_slurm += f'#SBATCH --partition=default_cpu	# Which queue it should run on.\n'
        utils.write_to_template(run_icon_path, icon_slurm, id='%SLURM%') 

        # Write ICON runtime info to the run script.
        icon_runtime = f'#> Source the config_cmaq file to set the run environment\n'
        icon_runtime += f'source {self.CMAQ_HOME}/config_cmaq.csh {self.compiler} {self.compiler_vrsn}\n'
        #> Code Version
        icon_runtime += f'set VRSN     = {self.icon_vrsn}\n'
        #> Application Name                    
        icon_runtime += f'set APPL       = {self.appl}\n'
        #> Initial conditions type [profile|regrid]
        icon_runtime += f'ICTYPE   = {self.icon_type}\n'
        #> check GRIDDESC file for GRID_NAME options
        icon_runtime += f'setenv GRID_NAME {self.grid_name}\n'
        #> grid description file path
        icon_runtime += f'setenv GRIDDESC {self.CMAQ_DATA}/{self.appl}/mcip/GRIDDESC\n'
        #> GCTP spheroid, use 20 for WRF-based modeling
        icon_runtime += f'setenv IOAPI_ISPH 20\n'
        #> turn on excess WRITE3 logging [ options: T | F ]
        icon_runtime += f'setenv IOAPI_LOG_WRITE F\n'
        #> support large timestep records (>2GB/timestep record) [ options: YES | NO ]     
        icon_runtime += f'setenv IOAPI_OFFSET_64 YES\n'
        #> output file directory   
        icon_runtime += f'OUTDIR   = {self.CMAQ_DATA}/{self.appl}/icon\n'
        #> define the model execution id
        icon_runtime += f'setenv EXECUTION_ID $EXEC\n'
        utils.write_to_template(run_icon_path, icon_runtime, id='%RUNTIME%')

        # Write input file info to the run script
        icon_files =  f'    setenv SDATE           {self.start_datetime.strftime("%Y%j")}\n'
        icon_files += f'    setenv STIME           {self.start_datetime.strftime("%H%M%S")}\n'
        icon_files += f'if ( $ICON_TYPE == regrid ) then\n'
        icon_files += f'    setenv CTM_CONC_1 {self.CMAQ_DATA}/{coarse_grid_appl}/output_{self.cctm_runid}/CCTM_CONC_{self.cctm_runid}_{self.start_datetime.strftime("%Y%m%d")}.nc\n'
        icon_files += f'    setenv MET_CRO_3D_CRS {self.CMAQ_DATA}/{coarse_grid_appl}/mcip/METCRO3D_{self.start_datetime.strftime("%y%m%d")}\n'
        icon_files += f'    setenv MET_CRO_3D_FIN {self.CMAQ_DATA}/{self.appl}/mcip/METCRO3D_{self.start_datetime.strftime("%y%m%d")}.nc\n'
        icon_files += f'    setenv INIT_CONC_1    "$OUTDIR/ICON_{self.icon_vrsn}_{self.appl}_{self.icon_type}_{self.start_datetime.strftime("%Y%m%d")} -v"\n'
        icon_files += f'endif\n'
        icon_files += f'if ( $ICON_TYPE == profile ) then\n'
        icon_files += f'    setenv IC_PROFILE $BLD/avprofile_cb6r3m_ae7_kmtbr_hemi2016_v53beta2_m3dry_col051_row068.csv\n'
        icon_files += f'    setenv MET_CRO_3D_FIN {self.CMAQ_DATA}/{self.appl}/mcip/METCRO3D_{self.start_datetime.strftime("%y%m%d")}.nc\n'
        icon_files += f'    setenv INIT_CONC_1    "$OUTDIR/ICON_{self.icon_vrsn}_{self.appl}_{self.icon_type}_{self.start_datetime.strftime("%Y%m%d")} -v"\n'
        icon_files += f'endif\n'
        utils.write_to_template(run_icon_path, icon_files, id='%INFILES%')

        ## RUN ICON
        if not setup_only:
            CMD_ICON = f'sbatch --requeue {run_icon_path}'
            os.system(CMD_ICON)
            # Sleep until the run_icon_{self.appl}.log file exists
            while not os.path.exists(f'{self.ICON_SCRIPTS}/run_icon_{self.appl}.log'):
                time.sleep(1)
            # Begin ICON simulation clock
            simstart = datetime.datetime.now()
            if self.verbose:
                print('Starting ICON at: ' + str(simstart))
                sys.stdout.flush()
            icon_sim = self.finish_check('icon')
            while icon_sim != 'complete':
                if icon_sim == 'failed':
                    return False
                else:
                    time.sleep(2)
                    icon_sim = self.finish_check('icon')
            elapsed = datetime.datetime.now() - simstart
            if self.verbose:
                print(f'ICON ran in: {utils.strfdelta(elapsed)}')
        return True

    def run_bcon(self, bcon_start_datetime=None, bcon_end_datetime=None, coarse_grid_appl='coarse', 
                 run_hours=2, setup_only=False):
        """
        Setup and run BCON, which produces boundary conditions for CMAQ.

        Parameters
        ----------
        :param bcon_start_datetime: string
            Start date and time for BCON. Defaults to None in which case the BCON start 
            datetime will be assigned from the CMAQ start datetime.
        :param bcon_end_datetime: string
            End date and time for BCON. Defaults to None in which case the BCON end 
            datetime will be assigned from the CMAQ end datetime.
        :param coarse_grid_appl: string
            Application name for the coarse grid from which you are deriving boundary conditions.
        :param run_hours: int
            Number of hours to request from the scheduler.
        :setup_only: bool
            Option to setup the directories and write the scripts without running BCON.
        """
        # Set the start and end dates
        if bcon_start_datetime is None:
            bcon_start_datetime = self.start_datetime
        else:
            bcon_start_datetime = utils.format_date(bcon_start_datetime)
        if bcon_end_datetime is None:
            bcon_end_datetime = self.end_datetime
        else:
            bcon_end_datetime = utils.format_date(bcon_end_datetime)
        # Determine the length of the BCON run
        bcon_delt = bcon_end_datetime - bcon_start_datetime

        # Define the coarse grid runid
        coarse_runid = f'{self.cctm_vrsn}_{self.compiler}{self.compiler_vrsn}_{coarse_grid_appl}'

        ## SETUP BCON
        # Copy the template BCON run script to the scripts directory
        run_bcon_path = f'{self.BCON_SCRIPTS}/run_bcon.csh'
        cmd = self.CMD_CP % (f'{self.DIR_TEMPLATES}/template_run_bcon.csh', run_bcon_path)
        os.system(cmd)

        # Specify the BCON log
        bcon_log_file = f'{self.BCON_SCRIPTS}/run_bcon_{self.appl}_{bcon_start_datetime.strftime("%Y%m%d")}.log'

        # Write Slurm info
        bcon_slurm =  f'#SBATCH -J bcon_{self.appl}		# Job name\n'
        bcon_slurm += f'#SBATCH -o {bcon_log_file}\n'
        bcon_slurm += f'#SBATCH --nodes=1		# Total number of nodes requested\n' 
        bcon_slurm += f'#SBATCH --ntasks=1		# Total number of tasks to be configured for.\n' 
        bcon_slurm += f'#SBATCH --tasks-per-node=1	# sets number of tasks to run on each node.\n' 
        bcon_slurm += f'#SBATCH --cpus-per-task=1	# sets number of cpus needed by each task.\n'
        bcon_slurm += f'#SBATCH --get-user-env		# tells sbatch to retrieve the users login environment.\n' 
        bcon_slurm += f'#SBATCH -t {run_hours}:00:00		# Run time (hh:mm:ss)\n' 
        bcon_slurm += f'#SBATCH --mem=20000M		# memory required per node\n'
        bcon_slurm += f'#SBATCH --partition=default_cpu	# Which queue it should run on.\n'
        utils.write_to_template(run_bcon_path, bcon_slurm, id='%SLURM%') 

        # Write BCON runtime info to the run script.
        bcon_runtime =  f'#> Source the config_cmaq file to set the run environment\n'
        bcon_runtime += f'source {self.CMAQ_HOME}/config_cmaq.csh {self.compiler} {self.compiler_vrsn}\n'
        bcon_runtime += f'#> Code Version\n'
        bcon_runtime += f'set VRSN     = {self.bcon_vrsn}\n'
        bcon_runtime += f'#> Application Name\n'                    
        bcon_runtime += f'set APPL     = {self.appl}\n'
        bcon_runtime += f'#> Boundary condition type [profile|regrid]\n'                     
        bcon_runtime += f'set BCTYPE   = {self.bcon_type}\n'
        bcon_runtime += f'#> check GRIDDESC file for GRID_NAME options\n'                 
        bcon_runtime += f'setenv GRID_NAME {self.grid_name}\n'
        bcon_runtime += f'#> grid description file\n'                    
        bcon_runtime += f'setenv GRIDDESC {self.GRIDDESC}\n'
        bcon_runtime += f'#> GCTP spheroid, use 20 for WRF-based modeling\n' 
        bcon_runtime += f'setenv IOAPI_ISPH 20\n'                     
        bcon_runtime += f'#> turn on excess WRITE3 logging [ options: T | F ]\n'
        bcon_runtime += f'setenv IOAPI_LOG_WRITE F\n'
        bcon_runtime += f'#> support large timestep records (>2GB/timestep record) [ options: YES | NO ]\n'     
        bcon_runtime += f'setenv IOAPI_OFFSET_64 YES\n'
        bcon_runtime += f'#> output file directory\n'   
        bcon_runtime += f'set OUTDIR   = {self.CMAQ_DATA}/{self.appl}/bcon\n'
        bcon_runtime += f'#> Set the build directory:\n'
        bcon_runtime += f'set BLD      = {self.CMAQ_HOME}/PREP/bcon/scripts/BLD_BCON_{self.bcon_vrsn}_{self.compiler}{self.compiler_vrsn}\n'
        bcon_runtime += f'set EXEC     = BCON_{self.bcon_vrsn}.exe\n'
        bcon_runtime += f'#> define the model execution id\n'
        bcon_runtime += f'setenv EXECUTION_ID $EXEC\n'
        utils.write_to_template(run_bcon_path, bcon_runtime, id='%RUNTIME%')    

        # Write input file info to the run script
        # bcon_files =  f'    setenv SDATE           {bcon_start_datetime.strftime("%Y%j")}\n'
        # bcon_files += f'    setenv STIME           {bcon_start_datetime.strftime("%H%M%S")}\n'
        # bcon_files += f'    setenv RUNLEN          {utils.strfdelta(bcon_delt, fmt="{H:02}{M:02}{S:02}")}\n'   
        
        bcon_files  = f' if ( $BCON_TYPE == regrid ) then\n'
        bcon_files += f'     setenv CTM_CONC_1 {self.CMAQ_DATA}/{coarse_grid_appl}/output_CCTM_{coarse_runid}/CCTM_CONC_{coarse_runid}_{bcon_start_datetime.strftime("%Y%m%d")}.nc\n'
        bcon_files += f'     setenv MET_CRO_3D_CRS {self.CMAQ_DATA}/{coarse_grid_appl}/mcip/METCRO3D_{bcon_start_datetime.strftime("%y%m%d")}.nc\n'
        bcon_files += f'     setenv MET_BDY_3D_FIN {self.CMAQ_DATA}/{self.appl}/mcip/METBDY3D_{bcon_start_datetime.strftime("%y%m%d")}.nc\n'
        bcon_files += f'     setenv BNDY_CONC_1    "$OUTDIR/BCON_{self.bcon_vrsn}_{self.appl}_{self.bcon_type}_{bcon_start_datetime.strftime("%Y%m%d")} -v"\n'
        bcon_files += f' endif\n'
        
        bcon_files += f' if ( $BCON_TYPE == profile ) then\n'
        bcon_files += f'     setenv BC_PROFILE $BLD/avprofile_cb6r3m_ae7_kmtbr_hemi2016_v53beta2_m3dry_col051_row068.csv\n'
        bcon_files += f'     setenv MET_BDY_3D_FIN {self.CMAQ_DATA}/{self.appl}/mcip/METBDY3D_{bcon_start_datetime.strftime("%y%m%d")}.nc\n'
        bcon_files += f'     setenv BNDY_CONC_1    "$OUTDIR/BCON_{self.bcon_vrsn}_{self.appl}_{self.bcon_type}_{bcon_start_datetime.strftime("%Y%m%d")} -v"\n'
        bcon_files += f' endif\n'
        utils.write_to_template(run_bcon_path, bcon_files, id='%INFILES%')
        
        ## RUN BCON
        if not setup_only:
            # Remove log from previous identical run
            os.system(self.CMD_RM % (bcon_log_file))
            # Submit BCON to the scheduler
            CMD_BCON = f'sbatch --requeue {run_bcon_path}'
            os.system(CMD_BCON)
            # Begin BCON simulation clock
            simstart = datetime.datetime.now()
            # Sleep until the run_bcon_{self.appl}.log file exists
            while not os.path.exists(bcon_log_file):   
                time.sleep(1)
            if self.verbose:
                print('Starting BCON at: ' + str(simstart))
                sys.stdout.flush()
            bcon_sim = self.finish_check('bcon', custom_log=bcon_log_file)
            while bcon_sim != 'complete':
                if bcon_sim == 'failed':
                    return False
                else:
                    time.sleep(2)
                    bcon_sim = self.finish_check('bcon', custom_log=bcon_log_file)
            elapsed = datetime.datetime.now() - simstart
            if self.verbose:
                print(f'BCON ran in: {utils.strfdelta(elapsed)}')
        return True

    def run_bcon_multiday(self, coarse_grid_appl='coarse', run_hours=2, setup_only=False):
        """
        Run BCON over multiple days. Per CMAQ convention, BCON will run for the same length
        as CCTM -- i.e., a single day. 

        Parameters
        ----------
        :param coarse_grid_appl: string
            Application name for the coarse grid from which you are deriving boundary conditions.
        :param run_hours: int
            Number of hours to request from the scheduler.
        :setup_only: bool
            Option to setup the directories and write the scripts without running BCON.
        """
        # Loop over each day
        for day_no in range(self.delt.days):
            # Set the start datetime and end datetime for the day
            bcon_start_datetime = self.start_datetime + datetime.timedelta(day_no)
            bcon_end_datetime = self.start_datetime + datetime.timedelta(day_no + 1)
            if self.verbose:
                print(f'--> Working on BCON for {bcon_start_datetime}')

            # run bcon for that day
            self.run_bcon(bcon_start_datetime=bcon_start_datetime, bcon_end_datetime=bcon_end_datetime,
                coarse_grid_appl=coarse_grid_appl, run_hours=run_hours, setup_only=setup_only)

    def setup_inpdir(self, n_emis_gr=2, gr_emis_labs=['all', 'rwc'], n_emis_pt=9, 
        pt_emis_labs=['ptnonertac', 'ptertac', 'othpt', 'ptagfire', 'ptfire', 'ptfire_othna', 'pt_oilgas', 'cmv_c3_12', 'cmv_c1c2_12'],
        stkgrps_daily=[False, False, False, True, True, True, False, False, False]):
        """
        Links all the necessary files to the locations in INPDIR where CCTM expects to find them.

        Parameters
        ----------
        :param n_emis_gr: int
            Number of gridded emissions sectors.
        :param gr_emis_labs: list of strings
            Labels for each of the gridded emissions sectors.
        :param n_emis_pt: int
            Number of point emissions sectors.
        :param pt_emis_labs: list of strings
            Labels for each of the point emissions sectors.
        :param stkgrps_daily: list of bools 
            Boolean indicating if each point sector uses daily stack groups files.
            For example, fire sectors use daily stack groups files.
        """
        # Remove the existing input directory if it already exists and remake it
        utils.remove_dir(self.CCTM_INPDIR)
        utils.make_dirs(self.CCTM_INPDIR)

        # Make a list of the start dates for date-specific inputs
        start_datetimes_lst = [single_date for single_date in (self.start_datetime + datetime.timedelta(n) for n in range(self.delt.days + 1))]

        # Make lists of representative days
        # These are necessary because some of the point sectors use representative days
        # Right now, this simply links the smoke merge dates, but it could actually use the representative days at some point in the future
        utils.make_dirs(f'{self.CCTM_INPDIR}/emis')
        cmd = 'echo "Starting to link files..."'
        for date in start_datetimes_lst:
            cmd = cmd + '; ' + self.CMD_LN % (f'{self.LOC_SMK_MERGE_DATES}/smk_merge_dates_{date.strftime("%Y%m")}*', f'{self.CCTM_INPDIR}/emis')
        os.system(cmd)
        mwdss_N_lst = utils.get_rep_dates(f'{self.LOC_SMK_MERGE_DATES}', start_datetimes_lst, date_type='  mwdss_N')
        mwdss_Y_lst = utils.get_rep_dates(f'{self.LOC_SMK_MERGE_DATES}', start_datetimes_lst, date_type='  mwdss_Y')

        # Link the GRIDDESC to $INPDIR
        cmd = self.CMD_LN % (self.GRIDDESC, f'{self.CCTM_INPDIR}/')
        cmd_gunzip = self.CMD_GUNZIP % (self.GRIDDESC)

        # Link Boundary Conditions to $INPDIR/icbc
        utils.make_dirs(self.ICBC)
        for date in start_datetimes_lst:
            local_bc_file = f'{self.LOC_BC}/*{date.strftime("%y%m%d")}'
            cmd = cmd + '; ' + self.CMD_LN % (local_bc_file, f'{self.ICBC}/')
            cmd_gunzip = cmd_gunzip + ' >/dev/null 2>&1; ' +  self.CMD_GUNZIP % (local_bc_file)
        
        # Link Initial Conditions to self.CCTM_OUTDIR
        utils.make_dirs(self.CCTM_OUTDIR)
        yesterday = start_datetimes_lst[0] - datetime.timedelta(days=1)
        local_ic_file = f'{self.LOC_IC}/CCTM_CGRID_*{yesterday.strftime("%Y%m%d")}.nc'
        cmd = cmd + '; ' + self.CMD_LN % (local_ic_file, f'{self.CCTM_OUTDIR}/CCTM_CGRID_{self.cctm_runid}_{yesterday.strftime("%Y%m%d")}.nc')
        local_init_medc_1_file = f'{self.LOC_IC}/CCTM_MEDIA_CONC_*{yesterday.strftime("%y%m%d")}.nc'
        cmd = cmd + '; ' + self.CMD_LN % (local_init_medc_1_file, f'{self.CCTM_OUTDIR}/CCTM_MEDIA_CONC_{self.cctm_runid}_{yesterday.strftime("%Y%m%d")}.nc')

        # Link gridded emissions to $INPDIR/emis/gridded_area
        utils.make_dirs(self.CCTM_GRIDDED)
        for ii in range(n_emis_gr + 1):
            # Get the name of the directory where theis gridded sector is stored
            gr_emis_dir = self.dirpaths.get(f'LOC_GR_EMIS_{str(ii).zfill(3)}')
            if self.verbose:
                print(f'Linking gridded emissions from:\n{gr_emis_dir}')
            for date in start_datetimes_lst:
                local_gridded_file = f'{gr_emis_dir}/emis_mole_{gr_emis_labs[ii-1]}_{date.strftime("%Y%m%d")}*'
                if self.verbose:
                    print(f'... Linking: {local_gridded_file}')
                cmd = cmd + '; ' + self.CMD_LN % (local_gridded_file, f'{self.CCTM_GRIDDED}/')
                cmd_gunzip = cmd_gunzip + ' >/dev/null 2>&1; ' +  self.CMD_GUNZIP % (local_gridded_file)

        # Link point source emissions to $INPDIR/emis/inln_point 
        # and the associated stack groups to $INPDIR/emis/inln_point/stack_groups
        utils.make_dirs(f'{self.CCTM_PT}/stack_groups')
        for ii in range(n_emis_pt + 1):
            if self.verbose:
                    print(f'Linking the {pt_emis_labs[ii-1]} sector emissions')
            for date in start_datetimes_lst:
                # Link the day-dependent point sector emissions file
                if pt_emis_labs[ii-1] == 'ptertac':
                    local_point_file = f'{self.LOC_ERTAC}/inln_mole_ptertac_{date.strftime("%Y%m%d")}*'
                else:
                    local_point_file = f'{self.LOC_IN_PT}/{pt_emis_labs[ii-1]}/inln_mole_{pt_emis_labs[ii-1]}_{date.strftime("%Y%m%d")}*'
                if self.verbose:
                    print(f'... Linking: {local_point_file}')
                cmd = cmd + '; ' + self.CMD_LN % (local_point_file, f'{self.CCTM_PT}/')
                cmd_gunzip = cmd_gunzip + ' >/dev/null 2>&1; ' +  self.CMD_GUNZIP % (local_point_file)
                # Link the day-dependent stack groups file (e.g., for fire sectors)
                if stkgrps_daily[ii-1]:
                    local_stkgrps_file = f'{self.LOC_IN_PT}/{pt_emis_labs[ii-1]}/stack_groups_{pt_emis_labs[ii-1]}_{date.strftime("%Y%m%d")}*'
                    cmd = cmd + '; ' + self.CMD_LN % (local_stkgrps_file, f'{self.CCTM_PT}/stack_groups/')
                    cmd_gunzip = cmd_gunzip + ' >/dev/null 2>&1; ' +  self.CMD_GUNZIP % (local_stkgrps_file)
            # Link the day-independent stack groups file
            if not stkgrps_daily[ii-1]:
                if pt_emis_labs[ii-1] == 'ptertac':
                    local_stkgrps_file = f'{self.LOC_ERTAC}/stack_groups_ptertac_*'
                else:
                    local_stkgrps_file = f'{self.LOC_IN_PT}/{pt_emis_labs[ii-1]}/stack_groups_{pt_emis_labs[ii-1]}_*'
                cmd = cmd + '; ' + self.CMD_LN % (local_stkgrps_file, f'{self.CCTM_PT}/stack_groups/')
                cmd_gunzip = cmd_gunzip + ' >/dev/null 2>&1; ' +  self.CMD_GUNZIP % (local_stkgrps_file)
        
        # Link sector list to $INPDIR/emis
        cmd = cmd + '; ' + self.CMD_LN % (f'{self.SECTORLIST}', f'{self.CCTM_INPDIR}/emis')

        # Link files for emissions scaling and sea spray to $INPDIR/land
        # NOTE: these could be made more general...
        utils.make_dirs(f'{self.CCTM_LAND}/toCMAQ_festc1.4_epic')
        for date in start_datetimes_lst:
            local_festc_file = f'{self.LOC_LAND}/toCMAQ_festc1.4_epic/us1_2016_cmaq12km_time20*{date.strftime("%y%m%d")}*'
            cmd = cmd + '; ' + self.CMD_LN % (local_festc_file, f'{self.CCTM_LAND}/toCMAQ_festc1.4_epic/')
            cmd_gunzip = cmd_gunzip + ' >/dev/null 2>&1; ' +  self.CMD_GUNZIP % (local_festc_file)
        cmd = cmd + '; ' + self.CMD_LN % (f'{self.LOC_LAND}/toCMAQ_festc1.4_epic/us1_2016_cmaq12km_soil.12otc2.ncf', f'{self.CCTM_LAND}/toCMAQ_festc1.4_epic/')
        cmd = cmd + '; ' + self.CMD_LN % (f'{self.LOC_LAND}/{self.filenames.get("OCEAN_1")}', f'{self.CCTM_LAND}/')
        cmd = cmd + '; ' + self.CMD_LN % (f'{self.LOC_LAND}/beld41_feb2017_waterfix_envcan_12US2.12OTC2.ncf', f'{self.CCTM_LAND}/')
        
        # Run the gunzip commands
        cmd_gunzip += ' >/dev/null 2>&1'
        os.system(cmd_gunzip)
        
        # Run the link commands
        os.system(cmd)

        # Remove broken links from the input dir
        os.system(f'find {self.CCTM_INPDIR} -xtype l -delete')    
    
    def run_cctm(self, n_emis_gr=2, gr_emis_labs=['all', 'rwc'], n_emis_pt=9, 
        pt_emis_labs=['ptnonertac', 'ptertac', 'othpt', 'ptagfire', 'ptfire', 'ptfire_othna', 'pt_oilgas', 'cmv_c3_12', 'cmv_c1c2_12'],
        stkgrps_daily=[False, False, False, True, True, True, False, False, False],
        ctm_abflux='Y',
        stkcaseg = '12US1_2016fh_16j', stkcasee = '12US1_cmaq_cb6_2016fh_16j', 
        delete_existing_output='TRUE', new_sim='FALSE', tstep='010000', 
        cctm_hours=24, n_procs=16, gb_mem=50, run_hours=24, setup_only=False):
        """
        Setup and run CCTM, CMAQ's chemical transport model.

        Parameters
        ----------
        :param n_emis_gr: int
            Number of gridded emissions sectors.
        :param gr_emis_labs: list of strings
            Labels for each of the gridded emissions sectors.
        :param n_emis_pt: int
            Number of point emissions sectors.
        :param pt_emis_labs: list of strings
            Labels for each of the point emissions sectors.
        :param stkgrps_daily: list of bools 
            Boolean indicating if each point sector uses daily stack groups files.
            For example, fire sectors use daily stack groups files. 
        :param ctm_abflux: string
            Turns on/off ammonia bi-directional flux for in-line deposition.
            Options are [Y, N].
        :param stkcaseg: string
            Stack group version label.
        :param stkcasee: string
            Stack emission version label
        :param delete_existing_output: string
            If TRUE, any files or logs previously created by CCTM will be deleted. 
            If FALSE, previous files or logs will cause CCTM to fail. Options are
            [TRUE, FALSE].
        :param new_sim: string
            Set to FALSE for model restart. Options are [TRUE, FALSE].
        :param tstep: string
            Output time step interval (HHMMSS). Defaults to 010000.
        :param cctm_hours: int
            Time duration for this run of CCTM in hours.
        :param n_procs: int
            Number of processors to request from the scheduler. 
        :param gb_mem: int
            Number of GB of memory per node to request from the scheduler.  
        :param run_hours: int
            Run length, in hours, to request from the scheduler.
        :param setup_only: bool
            Option to setup the directories and write the scripts without running CCTM.
        """
        # Check that a consistent number of labels were passed
        if len(gr_emis_labs) != n_emis_gr:
            raise ValueError(f'n_emis_gr ({n_emis_gr}) should match the length of gr_emis_labs (len={len(gr_emis_labs)})')
        if len(pt_emis_labs) != n_emis_pt:
            raise ValueError(f'n_emis_pt ({n_emis_pt}) should match the length of pt_emis_labs (len={len(pt_emis_labs)})')
        if len(stkgrps_daily) != n_emis_pt:
            raise ValueError(f'n_emis_pt ({n_emis_pt}) should match the length of stkgrps_daily (len={len(stkgrps_daily)})')
        ## SETUP CCTM
        # Copy the template CCTM run script to the scripts directory
        run_cctm_path = f'{self.CCTM_SCRIPTS}/run_cctm_{self.appl}.csh'
        cmd = self.CMD_CP % (f'{self.DIR_TEMPLATES}/template_run_cctm.csh', run_cctm_path)
        os.system(cmd)
        # Copy the template CCTM submission script to the scripts directory
        submit_cctm_path = f'{self.CCTM_SCRIPTS}/submit_cctm.csh'
        cmd = self.CMD_CP % (f'{self.DIR_TEMPLATES}/template_submit_cctm.csh', submit_cctm_path)
        os.system(cmd)
        # Setup the input directory using the setup_inpdir method
        self.setup_inpdir(n_emis_gr=n_emis_gr, gr_emis_labs=gr_emis_labs, 
            n_emis_pt=n_emis_pt, pt_emis_labs=pt_emis_labs,stkgrps_daily=stkgrps_daily)

        # Write CCTM setup options to the run script
        cctm_runtime =  f'#> Toggle Diagnostic Mode which will print verbose information to standard output\n'
        cctm_runtime += f'setenv CTM_DIAG_LVL 0\n'
        cctm_runtime += f'#> Source the config_cmaq file to set the run environment\n'
        cctm_runtime += f'source {self.CMAQ_HOME}/config_cmaq.csh {self.compiler} {self.compiler_vrsn}\n'
        cctm_runtime += f'#> Change back to the CCTM scripts directory\n'
        cctm_runtime += f'cd {self.CCTM_SCRIPTS}\n'
        cctm_runtime += f'#> Set General Parameters for Configuring the Simulation\n'
        cctm_runtime += f'set VRSN      = {self.cctm_vrsn}          #> Code Version - note this must be updated if using ISAM or DDM\n'
        cctm_runtime += f'set PROC      = mpi                       #> serial or mpi\n'
        cctm_runtime += f'set MECH      = {self.chem_mech}          #> Mechanism ID\n'
        cctm_runtime += f'set APPL      = {self.appl}               #> Application Name (e.g. Gridname)\n\n'
        cctm_runtime += f'#> Define RUNID as any combination of parameters above or others. By default,\n'
        cctm_runtime += f'#> this information will be collected into this one string, $RUNID, for easy\n'
        cctm_runtime += f'#> referencing in output binaries and log files as well as in other scripts.\n'
        cctm_runtime += f'setenv RUNID  {self.cctm_runid}\n\n'
        cctm_runtime += f'#> Set Working, Input, and Output Directories\n'
        cctm_runtime += f'setenv WORKDIR {self.CCTM_SCRIPTS}        #> Working Directory. Where the runscript is.\n'
        cctm_runtime += f'setenv OUTDIR  {self.CCTM_OUTDIR}         #> Output Directory\n'
        cctm_runtime += f'setenv INPDIR  {self.CCTM_INPDIR}         #> Input Directory\n'
        cctm_runtime += f'setenv GRIDDESC {self.GRIDDESC}           #> grid description file\n'
        cctm_runtime += f'setenv GRID_NAME {self.grid_name}         #> check GRIDDESC file for GRID_NAME options\n\n'
        cctm_runtime += f'#> Keep or Delete Existing Output Files\n'
        cctm_runtime += f'set CLOBBER_DATA = {delete_existing_output}\n'
        utils.write_to_template(run_cctm_path, cctm_runtime, id='%SETUP%')

        # Write CCTM start, end, and timestepping options to the run script
        cctm_time =  f'#> Set Start and End Days for looping\n'
        cctm_time += f'setenv NEW_START {new_sim}        #> Set to FALSE for model restart\n'
        cctm_time += f'set START_DATE = "{self.start_datetime.strftime("%Y-%m-%d")}"     #> beginning date\n'
        cctm_time += f'set END_DATE   = "{self.end_datetime.strftime("%Y-%m-%d")}"       #> ending date\n\n'
        cctm_time += f'#> Set Timestepping Parameters\n'
        cctm_time += f'set STTIME     = {self.start_datetime.strftime("%H%M%S")}         #> beginning GMT time (HHMMSS)\n'
        cctm_time += f'set NSTEPS     = {cctm_hours}0000                                 #> time duration (HHMMSS) for this run\n'
        cctm_time += f'set TSTEP      = {tstep}                                          #> output time step interval (HHMMSS)\n'
        utils.write_to_template(run_cctm_path, cctm_time, id='%TIME%')

        # Control domain subsetting among processors -- these will always be closest to a square
        if n_procs == 8:
            cctm_proc = '@ NPCOL  =  2; @ NPROW =  4'
        elif n_procs == 12:
            cctm_proc = '@ NPCOL  =  3; @ NPROW =  4'
        elif n_procs == 16:
            cctm_proc = '@ NPCOL  =  4; @ NPROW =  4'
        elif n_procs == 24:
            cctm_proc = '@ NPCOL  =  4; @ NPROW =  6'
        elif n_procs == 32:
            cctm_proc = '@ NPCOL  =  4; @ NPROW =  8'
        elif n_procs == 48:
            cctm_proc = '@ NPCOL  =  6; @ NPROW =  8'
        else:
            print(f'No {n_procs} processor setup has been specified. Use [8, 12, 16, 24, 32, or 48].')
            raise ValueError
        utils.write_to_template(run_cctm_path, cctm_proc, id='%PROC%')

        # Write CCTM physics information
        # NOTE: at some point the number of physics options should be expanded. 
        cctm_physics  = f'setenv CTM_ABFLUX {ctm_abflux}          #> ammonia bi-directional flux for in-line deposition\n' 
        cctm_physics += f'                             #>    velocities [ default: N ]\n'
        utils.write_to_template(run_cctm_path, cctm_physics, id='%PHYSICS%') 

        # Write CCTM input input directory information
        cctm_files  = f'set ICpath    = {self.CCTM_OUTDIR}                 #> initial conditions input directory\n' 
        cctm_files += f'set BCpath    = {self.ICBC}                        #> boundary conditions input directory\n'
        cctm_files += f'set IN_PTpath = {self.CCTM_PT}                     #> point source emissions input directory\n'
        cctm_files += f'set IN_LTpath = $INPDIR/lightning                  #> lightning NOx input directory\n'
        cctm_files += f'set METpath   = {self.MCIP_OUT}                    #> meteorology input directory\n' 
        cctm_files += f'#set JVALpath  = $INPDIR/jproc                     #> offline photolysis rate table directory\n'
        cctm_files += f'set OMIpath   = $BLD                               #> ozone column data for the photolysis model\n'
        cctm_files += f'set LUpath    = {self.CCTM_LAND}                   #> BELD landuse data for windblown dust model\n'
        cctm_files += f'set SZpath    = {self.CCTM_LAND}                   #> surf zone file for in-line seaspray emissions\n'
        utils.write_to_template(run_cctm_path, cctm_files, id='%FILES%')

        # Write CCTM IC and BC information
        # NOTE: the two spaces at the beginning of each of these lines are necessary 
        # because this is all happening inside a loop in the csh script.
        cctm_icbc  = f'   #> Initial conditions\n'
        cctm_icbc += f'   if ($NEW_START == true || $NEW_START == TRUE ) then\n'
        cctm_icbc += f'       setenv ICON_{self.icon_vrsn}_{self.appl}_{self.icon_type}_{self.start_datetime.strftime("%Y%m%d")}\n'
        cctm_icbc += f'       setenv INIT_MEDC_1 notused\n'
        cctm_icbc += f'   else\n'
        cctm_icbc += f'       set ICpath = $OUTDIR\n'
        cctm_icbc +=  '       setenv ICFILE CCTM_CGRID_${RUNID}_${YESTERDAY}.nc\n'
        cctm_icbc +=  '   #   setenv INIT_MEDC_1 $ICpath/CCTM_MEDIA_CONC_${RUNID}_${YESTERDAY}.nc\n'
        cctm_icbc += f'       setenv INIT_MEDC_1 notused\n'
        cctm_icbc += f'       setenv INITIAL_RUN N\n'
        cctm_icbc += f'   endif\n'
        cctm_icbc += f'   \n'
        cctm_icbc += f'   #> Boundary conditions\n'
        if self.new_bcon:
            cctm_icbc += f'   set BCFILE = BCON_{self.bcon_vrsn}_{self.appl}_{self.bcon_type}_$YYYYMMDD\n'
        else:
            cctm_icbc += f'   set BCFILE = {self.filenames.get("BCFILE")}\n'
        utils.write_to_template(run_cctm_path, cctm_icbc, id='%ICBC%')

        # Write CCTM ocean file information.
        # NOTE: the two spaces at the beginning of each of these lines are necessary 
        # because this is all happening inside a loop in the csh script.
        cctm_ocean  = f'   #> In-line sea spray emissions configuration\n'
        cctm_ocean += f'   setenv OCEAN_1 $SZpath/{self.filenames.get("OCEAN_1")} #> horizontal grid-dependent surf zone file\n'
        utils.write_to_template(run_cctm_path, cctm_ocean, id='%OCEAN%')

        # Write CCTM gridded emissions information
        # NOTE: the two spaces at the beginning of each of these lines are necessary 
        # because this is all happening inside a loop in the csh script.
        cctm_gr  = f'   #> Gridded Emissions Files\n'
        cctm_gr += f'   setenv N_EMIS_GR {n_emis_gr}                          #> Number of gridded emissions groups\n'
        for ii in range(1, n_emis_gr + 1):
            gr_emis_file = self.filenames.get(f'GR_EMIS_{str(ii).zfill(3)}')
            cctm_gr += f'   setenv GR_EMIS_{str(ii).zfill(3)} {self.CCTM_GRIDDED}/{gr_emis_file}\n'
            cctm_gr += f'   # Label each gridded emissions stream\n'
            cctm_gr += f'   setenv GR_EMIS_LAB_{str(ii).zfill(3)} {gr_emis_labs[ii-1]}\n'
            cctm_gr += f'   # Do not allow CMAQ to use gridded source files with dates that do not match the model date\n'
            cctm_gr += f'   setenv GR_EM_SYM_DATE_{str(ii).zfill(3)} F\n'
        utils.write_to_template(run_cctm_path, cctm_gr, id='%GRIDDED%')

        # Write CCTM point source emissions information
        # NOTE: the two spaces at the beginning of each of these lines are necessary 
        # because this is all happening inside a loop in the csh script.
        cctm_pt  = f'   #> In-line point emissions configuration\n'
        cctm_pt += f'   setenv N_EMIS_PT {n_emis_pt}                          #> Number of elevated source groups\n'
        cctm_pt += f'   set STKCASEG = {stkcaseg}                             # Stack Group Version Label\n'
        cctm_pt += f'   set STKCASEE = {stkcasee}                             # Stack Emission Version Label\n'
        for ii in range(1, n_emis_pt + 1):
            stk_emis_file = self.filenames.get(f'STK_EMIS_{str(ii).zfill(3)}')
            stk_grps_file = self.filenames.get(f'STK_GRPS_{str(ii).zfill(3)}')
            cctm_pt += f'   # Time-Independent Stack Parameters for Inline Point Sources\n'
            cctm_pt += f'   setenv STK_GRPS_{str(ii).zfill(3)} $IN_PTpath/stack_groups/{stk_grps_file}\n'
            cctm_pt += f'   # Time-Dependent Emissions file\n'
            cctm_pt += f'   setenv STK_EMIS_{str(ii).zfill(3)} $IN_PTpath/{stk_emis_file}\n'
            cctm_pt += f'   # Label Each Emissions Stream\n'
            cctm_pt += f'   setenv STK_EMIS_LAB_{str(ii).zfill(3)} {pt_emis_labs[ii-1]}\n'
            cctm_pt += f'   # Allow CMAQ to Use Point Source files with dates that do not match the internal model date\n'
            cctm_pt += f'   setenv STK_EM_SYM_DATE_{str(ii).zfill(3)} T\n'
        utils.write_to_template(run_cctm_path, cctm_pt, id='%POINT%')

        # Write CCTM submission script
        cctm_sub =  f'#!/bin/csh\n'
        cctm_sub += f'\n'
        cctm_sub += f'#SBATCH -J cctm_{self.appl}                  # Job name\n'
        # cctm_sub += f'#SBATCH -o {self.CCTM_SCRIPTS}/out.cctm_{self.appl}              # Name of stdout output file\n'
        cctm_sub += f'#SBATCH -o /dev/null              # Name of stdout output file\n'
        # cctm_sub += f'#SBATCH -e {self.CCTM_SCRIPTS}/errors.cctm_{self.appl}           # Name of stderr output file\n'
        cctm_sub += f'#SBATCH -e /dev/null           # Name of stderr output file\n'
        cctm_sub += f'#SBATCH --ntasks={n_procs}             # Total number of tasks to be configured for.\n'
        cctm_sub += f'#SBATCH --tasks-per-node={n_procs}     # sets number of tasks to run on each node.\n'
        cctm_sub += f'#SBATCH --cpus-per-task=1       # sets number of cpus needed by each task (if task is "make -j3" number should be 3).\n'
        cctm_sub += f'#SBATCH --get-user-env          # tells sbatch to retrieve the users login environment. \n'
        cctm_sub += f'#SBATCH -t {run_hours}:00:00             # Run time (hh:mm:ss)\n'
        cctm_sub += f'#SBATCH --mem={gb_mem}000M            # memory required per node\n'
        cctm_sub += f'#SBATCH --partition=default_cpu # Which queue it should run on.\n'
        cctm_sub += f'\n'
        cctm_sub += f'{self.CCTM_SCRIPTS}/run_cctm_{self.appl}.csh >&! {self.CCTM_SCRIPTS}/cctm_{self.appl}.log\n'
        utils.write_to_template(submit_cctm_path, cctm_sub, id='%ALL%')

        if self.verbose:
            print('Done writing CCTM scripts!\n')
        
        ## RUN CCTM
        if not setup_only:
            # Remove logs from previous runs
            os.system(self.CMD_RM % (f'{self.CCTM_SCRIPTS}/CTM_LOG*{self.appl}*'))
            # Submit CCTM to Slurm
            CMD_CCTM = f'sbatch --requeue {submit_cctm_path}'
            os.system(CMD_CCTM)
            # Give the log a few seconds to reset itself.
            time.sleep(10)
            # Sleep until the run_cctm_{self.appl}.log file exists
            while not os.path.exists(f'{self.CCTM_SCRIPTS}/cctm_{self.appl}.log'):
                time.sleep(1)
            # Begin CCTM simulation clock
            simstart = datetime.datetime.now()
            if self.verbose:
                print('Starting CCTM at: ' + str(simstart))
                sys.stdout.flush()
            cctm_sim = self.finish_check('cctm')
            while cctm_sim != 'complete':
                if cctm_sim == 'failed':
                    return False
                else:
                    time.sleep(2)
                    cctm_sim = self.finish_check('cctm')
            elapsed = datetime.datetime.now() - simstart
            if self.verbose:
                print(f'CCTM ran in: {utils.strfdelta(elapsed)}')
                sys.stdout.flush()
        return True

    def run_combine(self, run_hours=2, mem_per_node=20, combine_vrsn='v532'):
        """
        Setup and run the combine program. Combine is a CMAQ post-processing program that formats 
        the CCTM output data in a more convenient way.

        Parameters
        ----------
        :param run_hours: int
            Run length, in hours, to request from the scheduler.
        :param mem_per_node: int
            Number of GB of memory per node to request from the scheduler. 
        :param combine_vrsn: string
            Version number of combine for identifying executables. 
        """
        ## Setup Combine
        # Copy the template combine run script to the scripts directory
        run_combine_path = f'{self.COMBINE_SCRIPTS}/run_combine.csh'
        cmd = self.CMD_CP % (f'{self.DIR_TEMPLATES}/template_run_combine.csh', run_combine_path)
        os.system(cmd)

        # Write slurm info
        combine_slrum =  f'#SBATCH -J combine_{self.appl}              # Job name\n'
        combine_slrum += f'#SBATCH -o {self.COMBINE_SCRIPTS}/out_combine_{self.appl}.log   # Name of stdout output file\n'
        combine_slrum += f'#SBATCH --ntasks=1              # Total number of tasks\n'
        combine_slrum += f'#SBATCH --tasks-per-node=1      # sets number of tasks to run on each node\n'
        combine_slrum += f'#SBATCH --cpus-per-task=1       # sets number of cpus needed by each task\n'
        combine_slrum += f'#SBATCH --get-user-env          # tells sbatch to retrieve the users login environment\n'
        combine_slrum += f'#SBATCH -t {run_hours}:00:00              # Run time (hh:mm:ss)\n'
        combine_slrum += f'#SBATCH --mem={mem_per_node}000M            # memory required per node\n'
        combine_slrum += f'#SBATCH --partition=default_cpu # Which queue it should run on\n'
        utils.write_to_template(run_combine_path, combine_slrum, id='%SLURM%') 

        # Write runtime info
        combine_runtime =  f'#> Choose compiler and set up CMAQ environment with correct\n'
        combine_runtime += f'#> libraries using config.cmaq. Options: intel | gcc | pgi\n'
        combine_runtime += f'setenv compiler {self.compiler}\n'
        combine_runtime += f'setenv compilerVrsn {self.compiler_vrsn}\n' 
        combine_runtime += f'\n'
        combine_runtime += f'#> Source the config.cmaq file to set the build environment\n'
        combine_runtime += f'source {self.CMAQ_HOME}/config_cmaq.csh {self.compiler} {self.compiler_vrsn}\n'
        combine_runtime += f'\n'
        combine_runtime += f'#> Set General Parameters for Configuring the Simulation\n'
        combine_runtime += f'set VRSN      = {self.cctm_vrsn}              #> Code Version\n'
        combine_runtime += f'set PROC      = mpi               #> serial or mpi\n'
        combine_runtime += f'set MECH      = {self.chem_mech}      #> Mechanism ID\n'
        combine_runtime += f'set APPL      = {self.appl}        #> Application Name (e.g. Gridname)\n'
        combine_runtime += f'\n'
        combine_runtime += f'#> Define RUNID as any combination of parameters above or others. By default,\n'
        combine_runtime += f'#> this information will be collected into this one string, $RUNID, for easy\n'
        combine_runtime += f'#> referencing in output binaries and log files as well as in other scripts.\n'
        combine_runtime += f'set RUNID = {self.cctm_runid}\n'
        combine_runtime += f'\n'
        combine_runtime += f'#> Set the build directory if this was not set above\n' 
        combine_runtime += f'#> (this is where the CMAQ executable is located by default).\n'
        combine_runtime += f'if ( ! $?BINDIR ) then\n'
        combine_runtime += f'set BINDIR = {self.COMBINE_SCRIPTS}/BLD_combine_{combine_vrsn}_{self.compiler}{self.compiler_vrsn}\n'
        combine_runtime += f'endif\n'
        combine_runtime += f'\n'
        combine_runtime += f'#> Set the name of the executable.\n'
        combine_runtime += f'set EXEC = combine_{combine_vrsn}.exe\n'
        combine_runtime += f'\n'
        combine_runtime += f'#> Set location of CMAQ repo.  This will be used to point to the correct species definition files.\n'
        combine_runtime += f'set REPO_HOME = {self.CMAQ_HOME}\n'
        combine_runtime += f'\n'
        combine_runtime += f'#> Set working, input and output directories\n'
        combine_runtime += f'set METDIR     = {self.MCIP_OUT}           #> Met Output Directory\n'
        combine_runtime += f'set CCTMOUTDIR = {self.CCTM_OUTDIR}      #> CCTM Output Directory\n'
        combine_runtime += f'set POSTDIR    = {self.POST}                      #> Location where combine file will be written\n'
        utils.write_to_template(run_combine_path, combine_runtime, id='%RUNTIME%') 

        combine_setup =  f'#> Set Start and End Days for looping\n'
        combine_setup += f'set START_DATE = "{self.start_datetime.strftime("%Y-%m-%d")}"     #> beginning date\n'
        combine_setup += f'set END_DATE   = "{self.end_datetime.strftime("%Y-%m-%d")}"     #> ending date\n'
        combine_setup += f'\n'
        combine_setup += f'#> Set location of species definition files for concentration and deposition species.\n'
        combine_setup += f'setenv SPEC_CONC {self.COMBINE_SCRIPTS}/spec_def_files/SpecDef_{self.chem_mech}.txt\n'
        combine_setup += f'setenv SPEC_DEP  {self.COMBINE_SCRIPTS}/spec_def_files/SpecDef_Dep_{self.chem_mech}.txt\n'
        utils.write_to_template(run_combine_path, combine_setup, id='%SETUP%') 

        # Submit combine to slurm
        CMD_COMBINE = f'sbatch --requeue {run_combine_path}'
        os.system(CMD_COMBINE)

    def finish_check(self, program, custom_log=None):
        """
        Check if a specified CMAQ subprogram has finished running.

        Parameters
        ----------
        :param program: string
            CMAQ subprogram name whose status is to be checked.
        :param custom_log: string
            Path to a log file with a name that's different than those assigned 
            in the class methods. Defaults to None.
        :return: string 'running' or 'complete' or 'failed'
            Run status of the program.
        """
        if program == 'mcip':
            if custom_log is not None:
                msg = utils.read_last(custom_log, n_lines=1)
            else:
                msg = utils.read_last(f'{self.MCIP_SCRIPTS}/run_mcip_{self.mcip_appl}.log', n_lines=1)
            complete = 'NORMAL TERMINATION' in msg
            failed = 'Error running mcip' in msg
        elif program == 'icon':
            if custom_log is not None:
                msg = utils.read_last(custom_log, n_lines=20)
            else:
                msg = utils.read_last(f'{self.ICON_SCRIPTS}/run_icon_{self.appl}.log', n_lines=10)
            complete = '>>---->  Program  ICON completed successfully  <----<<' in msg
            failed = '*** ERROR ABORT' in msg
        elif program == 'bcon':
            if custom_log is not None:
                msg = utils.read_last(custom_log, n_lines=10)
            else:
                msg = utils.read_last(f'{self.BCON_SCRIPTS}/run_bcon_{self.appl}.log', n_lines=10)
            complete = '>>---->  Program  BCON completed successfully  <----<<' in msg
            failed = '*** ERROR ABORT' in msg
        elif program == 'cctm':
            if custom_log is not None:
                msg = utils.read_last(custom_log, n_lines=40)
            else:
                msg = utils.read_last(f'{self.CCTM_SCRIPTS}/cctm_{self.appl}.log', n_lines=40)
            complete = '|>---   PROGRAM COMPLETED SUCCESSFULLY   ---<|' in msg
            failed = 'Runscript Detected an Error' in msg
        else:
            complete = False
            failed = False
        if failed:
            print(f'\nCMAQPyError: {program} has failed. Last message was:\n{msg}')
            return 'failed'
        elif complete:
            return 'complete'
        else:
            return 'running'
            