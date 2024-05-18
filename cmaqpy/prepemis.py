"""
Functions to help prepare emissions for CMAQ.
"""

import pandas as pd

def fmt_like_camd(data_file='./pred_xg_co2.csv', lu_file='./RGGI_to_NYISO.csv'):
    """
    Takes data output from either the NY Simple Net or the ML Emissions Estimator, 
    and formats it for input into CAMD.

    Parameters
    ----------
    :param data_file: string
        File containing emissions data for a single pollutant throughout time.
    :param lu_file: string
        File containing the look-up table to convert from EPA ORISPL and Unit ID
        to the NYISO ID and Name.
    :return fmt_data_df: `pandas.DataFrame`
        Data with formating matching that of the emissions data from EPA CAMD.
    """
    # Read in data 
    raw_data_df = pd.read_csv(data_file, parse_dates=['TimeStamp'], infer_datetime_format=True)
    raw_data_df = raw_data_df.set_index('TimeStamp')
    # Read the lookup file
    lu_df = pd.read_csv(lu_file, header=1)
    lu_df = lu_df.drop(columns=['Notes', 'Unnamed: 6'])
    # Drop unnecessary units from the lookup df
    fmt_data_df = lu_df[lu_df['NYISO Name'].isin(raw_data_df.columns)].reset_index(drop=True)
    # Format the final dataset
    fmt_data_df = pd.concat([fmt_data_df, pd.DataFrame(index=fmt_data_df.index, columns=raw_data_df.index.values)], axis=1)
    # Create a generation dataframe for each ORISPL, UNIT ID combination
    for name in fmt_data_df['NYISO Name']:
        # Get simple net generation 
        unit_data = raw_data_df[name]
        # Determine how many units are associated with this name
        unit_bool = fmt_data_df['NYISO Name'] == name
        n_units = sum(unit_bool)
        # Edit the simple net generation based on this number of units
        unit_data = unit_data / n_units
        # Fill this unit gen profile into all matching units
        for idx in unit_bool[unit_bool].index.values:
            fmt_data_df.loc[idx, unit_data.index] = unit_data

    # Change the ORISPL to a string
    fmt_data_df = fmt_data_df.astype({'ORISPL': 'int'})
    fmt_data_df = fmt_data_df.astype({'ORISPL': 'str'})

    return fmt_data_df
    

def fmt_calc_hourly_base(base_file='calc_hourly_base.csv'):
    """
    Format the calc_hourly_base.csv file output by the ERTAC EGU preprocessor.

    Parameters
    ----------
    :param base_file: string
        Full path for the `calc_hourly_base.csv` file.
    :return base_df: `pandas.DataFrame`
        DataFrame containing the properly formatted emissions data
        from the `calc_hourly_base.csv` file.
    """
    # Read in the generator data previously preprocessed by ERTAC EGU tool
    base_df = pd.read_csv(base_file, dtype={'ertac_region': 'object',
                                            'ertac_fuel_unit_type_bin': 'object',
                                            'state': 'object',
                                            'facility_name': 'object',
                                            'orispl_code': 'int64',
                                            'unitid': 'object',
                                            'op_date': 'object',
                                            'op_hour': 'str',
                                            'op_time': 'float64',
                                            'gload (MW-hr)': 'object',
                                            'sload (1000 lbs)': 'float64',
                                            'so2_mass (lbs)': 'object',
                                            'so2_mass_measure_flg': 'object',
                                            'so2_rate (lbs/mmBtu)': 'float64',
                                            'so2_rate_measure_flg': 'object',
                                            'nox_rate (lbs/mmBtu)': 'float64',
                                            'nox_rate_measure_flg': 'object',
                                            'nox_mass (lbs)': 'object',
                                            'nox_mass_measure_flg': 'object',
                                            'co2_mass (tons)': 'object',
                                            'co2_mass_measure_flg': 'object',
                                            'co2_rate (tons/mmBtu)': 'float64',
                                            'co2_rate_measure_flg': 'object',
                                            'heat_input (mmBtu)': 'float64'})
    # Change the orispl_code to a string
    base_df = base_df.astype({'orispl_code': 'str'})
    # Pad the string for formatting
    base_df['op_hour'] = base_df['op_hour'].str.zfill(2)
    # Add a datetime column 
    base_df['datetime'] = pd.to_datetime(base_df['op_date'] + ' ' + base_df['op_hour'])

    return base_df


def update_camd(in_emis_file='calc_hourly_base.csv', co2_file='pred_xg_co2.csv', 
                nox_file='pred_xg_nox.csv', so2_file='pred_xg_so2.csv', 
                gen_file='thermal_without_renewable.csv', lu_file='RGGI_to_NYISO.csv', 
                out_emis_file='Updated_calc_hourly_base.csv'):
    """
    Update the CAMD load and emissions data with that generated from the NY Simple Net 
    and the ML-based emissions estimates. 

    Parameters
    ----------
    :param in_emis_file: string
        Path to baseline emissions file (i.e., ERTAC EGU `calc_hourly_base.csv`) 
    :param co2_file: string
        Path to the file containing the unit-level CO2 emissions.
    :param nox_file: string
        Path to the file containing the unit-level NOx emissions.
    :param so2_file: string
        Path to the file containing the unit-level SO2 emissions.
    :param gen_file: string
        Path to the file containing the unit-level power generation.
    :param lu_file: string
        Path to the file containing the look-up table to convert from
        EPA ORISPL and Unit ID to the NYISO ID and Name. 
    :param out_emis_file: string
        Path where the updated `calc_hourly_base.csv` file will be written.
    """
    # Read in the base emissions file
    base_df = fmt_calc_hourly_base(base_file=in_emis_file)
    # Read in ML CO2 emissions estimations
    ml_co2 = fmt_like_camd(data_file=co2_file, lu_file=lu_file)
    # Read in ML NOx emissions estimations
    ml_nox = fmt_like_camd(data_file=nox_file, lu_file=lu_file)
    # Read in ML SO2 emissions estimations
    ml_so2 = fmt_like_camd(data_file=so2_file, lu_file=lu_file)
    # Read in NY Simple Net generation
    ed_gen = fmt_like_camd(data_file=gen_file, lu_file=lu_file)
    
    # Get the name of an individual EGU -- this is how units are identified in the NY Simple Net & the ML
    for idx in ml_co2.index:
        # Get the ORISPL and the Unit ID
        egu_orispl = ml_co2.loc[idx].ORISPL
        egu_unitid = ml_co2.loc[idx]['Unit ID']
        print(f'Working on ORISPL: {egu_orispl}\tUNIT ID:{egu_unitid}')

        # Extract this ORISPL and UNIT ID from the base DataFrame
        egu_df = base_df.loc[(base_df['orispl_code'] == egu_orispl) & (base_df['unitid'] == egu_unitid)]
        # Extract the correct time window
        egu_df = egu_df.loc[base_df['datetime'].isin(ml_co2.columns[5:])]
        if len(egu_df) == 0:
            print('Warning: this unit was not found in the CAMD data... skipping')
        else:
            # Replace the CO2 emissions values
            # NOTE: this is probably a dangerous way of doing this -- might be better to add the datetime as another index in the egu_df
            egu_df['co2_mass (tons)'] = ml_co2.loc[idx, ml_co2.columns[5:]].values
            # Replace the SO2 emissions values
            egu_df['so2_mass (lbs)'] = ml_so2.loc[idx, ml_so2.columns[5:]].values
            # Replace the NOx emissions values
            egu_df['nox_mass (lbs)'] = ml_nox.loc[idx, ml_nox.columns[5:]].values
            # Replace the load values
            egu_df['gload (MW-hr)'] = ed_gen.loc[idx, ed_gen.columns[5:]].values
            # Combine this new unit data back into the base_df
            base_df.update(egu_df)

    # Save the updated emissions to a new CSV 
    # (after dropping the datetime column that we added)
    base_df = base_df.drop(columns=['datetime'])
    base_df.to_csv(out_emis_file, index=False) 
