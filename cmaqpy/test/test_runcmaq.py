"""
Tests runcmaq functions without running the CMAQ subprograms.
"""
import os
from cmaqpy.runcmaq import CMAQModel
import cmaqpy.utils as utils

start_datetime = 'Dec 31, 2011'
end_datetime = 'Jan 01, 2012'
appl = '2011_09NE'
coord_name = 'LamCon_111N_148W'
grid_name = '09NE'


def test_CMAQModel():
    """
    Checks that the CMAQModel class can be initialized correctly.
    """
    cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name)
    assert cmaq_sim.CMAQ_HOME == '/home/jas983/models/cmaq/CMAQ_v5.3.3'
    assert cmaq_sim.DIR_TEMPLATES == '/share/mzhang/jas983/cmaq_data/CMAQ_v5.3.3/cmaqpy/templates'
    assert cmaq_sim.start_datetime.strftime('%b %d, %Y') == start_datetime
    assert cmaq_sim.end_datetime.strftime('%b %d, %Y') == end_datetime


def test_run_mcip():
    """
    Tests the MCIP setup including the writing of the run script.
    """
    # Create a CMAQModel object
    cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name, verbose=True)
    # Specify the meteorolocial files
    metfile_list = ['wrfout_d01_2018-01-01_00:00:00', 'wrfout_d01_2018-01-07_22:40:30']
    # Call the "run_mcip" method in "setup_only" mode
    cmaq_sim.run_mcip(metfile_list=metfile_list, geo_file='geo_em.d01.nc', t_step=60, setup_only=True)
    assert os.path.exists(f'{cmaq_sim.MCIP_SCRIPTS}/run_mcip.csh') == 1


def test_run_icon():
    """
    Tests the ICON setup and writes the run script.
    """
    # Create a CMAQModel object
    cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name, verbose=True)
    # Call the "run_icon" method in "setup_only" mode
    cmaq_sim.run_icon(type='regrid', coarse_grid_name='32NE', cctm_pfx='CCTM_CONC_v53_', setup_only=True)
    assert os.path.exists(f'{cmaq_sim.ICON_SCRIPTS}/run_icon.csh') == 1


def test_run_bcon():
    """
    Tests the BCON setup and writes the run script.
    """
    # Create a CMAQModel object
    cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name, verbose=True)
    # Call the "run_icon" method in "setup_only" mode
    cmaq_sim.run_bcon(type='regrid', coarse_grid_name='32NE', cctm_pfx='CCTM_CONC_v53_', setup_only=True)
    assert os.path.exists(f'{cmaq_sim.BCON_SCRIPTS}/run_bcon.csh') == 1


def test_run_cctm():
    """
    Tests the CCTM setup and writes the run script.
    """
    # Create a CMAQModel object
    cmaq_sim = CMAQModel(start_datetime, end_datetime, appl, coord_name, grid_name, verbose=True)
    # Call the "run_icon" method in "setup_only" mode
    cmaq_sim.run_cctm(cctm_vrsn='v533', delete_existing_output='TRUE', new_sim='TRUE', tstep='010000', n_procs=16, setup_only=True)
    assert os.path.exists(f'{cmaq_sim.CCTM_SCRIPTS}/run_cctm.csh') == 1
    assert os.path.exists(f'{cmaq_sim.CCTM_SCRIPTS}/submit_cctm.csh') == 1
