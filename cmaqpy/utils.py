"""
Functions that support other cmaqpy modules.

Known Issues/Wishlist:

"""
import datetime
import os
import pandas as pd
import string
from shutil import rmtree


def format_date(in_date):
    """
    Formats an input date so that it can be correctly written to the namelist.

    Parameters
    ----------
    :param in_date : string
        string specifying the date
    :return: datetime64 array specifying the date
    """
    for fmt in ('%b %d %Y', '%B %d %Y', '%b %d, %Y', '%B %d, %Y',
                '%m-%d-%Y', '%m.%d.%Y', '%m/%d/%Y',
                '%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d',
                '%b %d %Y %H', '%B %d %Y %H', '%b %d, %Y %H', '%B %d, %Y %H',
                '%m-%d-%Y %H', '%m.%d.%Y %H', '%m/%d/%Y %H'):
        try:
            return datetime.datetime.strptime(in_date, fmt)
        except ValueError:
            pass
    raise ValueError('No valid date format found; please use a common US format (e.g., Jan 01, 2011 00)')


def strfdelta(tdelta, fmt='{H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """
    Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    Parameters
    ----------
    :param tdelta: datetime.timedelta object
        defining the difference in time that you would like to format.
    :param fmt: string
        allows custom formatting to be specified.  Fields can include
        seconds, minutes, hours, days, and weeks.  Each field is optional.

        Some examples:
            '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s'
            '{H:02}:{M:02}:{S:02}'            --> '01:44:33' (default)
            '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
            '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
            '{H}h {S}s'                       --> '72h 800s'.
    :param inputtype: string (default=timedelta)
        allowsing tdelta to be a regular number instead of the default,
        which is a datetime.timedelta object.  Valid inputtype strings:
            's', 'seconds',
            'm', 'minutes',
            'h', 'hours',
            'd', 'days',
            'w', 'weeks'.
    :return string
        formated to specification.

    """
    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = string.Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)


def write_to_template(template_path, txt_to_write, id='%REPLACE_HERE%'):
    """
    Replace a placeholder ID within a template file with desired text.

    Parameters
    ----------
    :param template_path: string
        Full path to the template file. You'll want to copy the template 
        file from the `cmaqpy/templates` directory, so you can reuse the 
        template. 
    :param txt_to_write: string
        Text to be written to the template file. Note that you can include
        comments, line breaks, etc. 
    :param id: string
        Identifier that will be overwritten with the text contained within 
        the `text_to_write` parameter. Obviously, this string should be unique
        so you don't accidentally overwrite the wrong thing. 
    """
    try:
        with open(template_path, 'r') as template:
            # Read the file into memory
            old_data = template.read()
            # Write new text in the location specified by the "id"
            new_data = old_data.replace(id, txt_to_write)
        with open(template_path, 'w') as script:
            # Overwrite the old file
            script.write(new_data)
    except IOError as e:
        print(f'Problem reading {template_path}')
        print(f'\t{e}')
    

def read_script(file):
    """
    Opens a namelist file within a context manager.

    Parameters
    ----------
    :param file: string
        Path to the namelist file you wish to open.
    :return: file object
    """
    with open(file, 'r') as script:
        return script.read()


def read_last(file_name, n_lines=1):
    """
    Reads the last line of a file.

    Parameters
    ----------
    :param file_name: string
        Complete path of the file that you would like read.
    :return last_line: string
        Last line of the input file.
    """
    try:
        with open(file_name, mode='r') as infile:
            lines = infile.readlines()
    except IOError:
        last_lines = 'IOEror in read_last_line: this file does not exist.'
        return last_lines
    try:
        last_lines = lines[-n_lines:]
        last_lines = '\n'.join(last_lines)
    except IndexError:
        last_lines = 'IndexError in read_last_line: no last line appears to exist in this file.'
    return last_lines


def remove_dir(directory, verbose=False):
    """
    This function utilized an exception clause to delete a directory.

    Parameters
    ----------
    :param directory: string
        complete path to the directory to be removed.
    :param verbose: boolean (default=False)
        determining whether or not to print lots of model information to the screen.
    """
    try:
        rmtree(directory)
    except OSError as e:
        if verbose:
            print(f"OSError in remove_dir: {e.filename} - {e.strerror}.")


def make_dirs(directory):
    """
    Checks if a directory exists and creates it if it doesn't.

    Parameters
    ----------
    :param directory: string
        complete path to the directory to be created. 
    """
    if not os.path.exists(directory):
        os.makedirs(directory, 0o755)


def get_rep_dates(smk_dates_dir, dates_list, date_type='  mwdss_N'):
    """
    Get representative dates from the files produced by smkmerge.

    Make sure that you include the correct white space in the date_type
    parameter. The options are: 
    ' aveday_N', ' aveday_Y', 
    '  mwdss_N', '  mwdss_Y', 
    '   week_N', '   week_Y', 
    '      all'

    NOTE: this woudld be slightly faster if I didn't reopen the file each time, 
    but it's such a small fraction of the time for CCTM that I'm not
    going to worry about it now.

    Parameters
    ----------
    :param smk_dates_dir: string
        Full path to the directory where the smoke merge date text files are located.
    :param date_list: list of `Timestamp` (or `datetime.datetime`)
        Simulation dates for which you want the corresponding representative dates.
    :param date_type: string
        Label from the `smk_merge_dates_YYYYMM.txt` file that you want to extract. 
        Note that SMOKE appends white space to the beginning of these, so you have 
        to include this white space for this function to run successfully (see function
        header).
    :retrun: `pandas.DatetimeIndex`
        Index of representative dates. 
    """
    rep_days = []
    # Loop through each day in the input list and append the respective representative day to the list
    for date in dates_list:
        d_str = date.strftime("%Y%m")
        smk_dates = pd.read_csv(f'{smk_dates_dir}/smk_merge_dates_{d_str}.txt', index_col=0, parse_dates=[0], infer_datetime_format=True)
        s = smk_dates[date_type]
        rep_days.append(s[date])

    # Remove duplicates in the represenatitive days 
    result = [] 
    [result.append(x) for x in rep_days if x not in result]

    # Convert to datetimes
    result = pd.to_datetime(result, format='%Y%m%d') 
    
    return result


def convert_tz_xr(ds, input_tz='UTC', output_tz='US/Eastern', time_coord='time'):
    """
    Converts an xarray dataset from one timezone to another.

    Note that this will not work if you have problematic date features within your 
    simulation (e.g., time changes). This is why xarray hasn't integrated this feature yet. 

    Parameters
    ----------
    :param ds: `xarray.DataSet`
        DataSet that you want converted from one time zone to another.
    :param input_tx: string
        String identifying the current time zone of the DataSet.
    :param output_tx: string
        String identifying the desired time zone of the DataSet.
    :param time_coord: string
        Name of the coordinate holding date/time information within `xarray.DataSet`
        that you passed in with `ds`.
    :return: `xarray.DataSet`
        DataSet with updated time zone reflected in the time coordinate. 
    """
    tidx_in = ds.time.to_index().tz_localize(tz=input_tz)
    ds.coords[time_coord] = tidx_in.tz_convert(output_tz).tz_localize(None)
    return ds
