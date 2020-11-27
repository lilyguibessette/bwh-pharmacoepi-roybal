import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil import parser, tz
import pickle
import os
import re


def import_redcap(run_time):
    import_date = run_time.date()
    # Imports REDCap patients that are enrolling on an ongoing basis as a pandas data frame from a CSV
    redcap_filepath = str(import_date) + "_redcap" + '.csv'
    fp = os.path.join("..", "..", "REDCap", redcap_filepath)
    date_cols = ["start_date"]
    # Reads in the csv file into a pandas data frame and ensures that the date_cols are imported as datetime.datetime objects
    # TODO potentially need to be careful here due to use of the data in redcap.py -> might want to ensure record_id column is a string, currently I think it defaults to an int
    redcap = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    redcap = redcap_vars_converter(redcap)
    # Returns the pandas dataframe of REDCap patient data that is read in
    # Note: The REDCap data does not contain observed feedback.
    # Hence why we do not overwrite our previous patient dictionary based on this data.
    # This is used to update patient dictionary data about:
    #   -   Whether patients are censored (i.e. due to death, consent withdrawal,
    #   -   Changes in Pillsy medications that a patient is taking
    #   -   Add entirely new patients initiating in the study to our patient dictionary by creating new patient objects
    return redcap


# For a DataFrame a dict can specify that different values should be replaced in different columns. For example, {'a': 1, 'b': 'z'} looks for the value 1 in column ‘a’ and the value ‘z’ in column ‘b’ and replaces these values with whatever is specified in value. The value parameter should not be None in this case. You can treat this as a special case of passing two lists except that you are specifying the column to search in.

def redcap_vars_converter(redcap_df):
    #Tested
    redcap_df = redcap_df.replace({'age': 1}, "18-34")
    redcap_df = redcap_df.replace({'age': 2}, "35-44")
    redcap_df = redcap_df.replace({'age': 3}, "45-54")
    redcap_df = redcap_df.replace({'age': 4}, "55-64")
    redcap_df = redcap_df.replace({'age': 5}, "65-74")
    redcap_df = redcap_df.replace({'age': 6}, "75-84")
    redcap_df = redcap_df.replace({'sex': 1}, "F")
    redcap_df = redcap_df.replace({'sex': 2}, "M")
    redcap_df = redcap_df.replace({'sex': 0}, "Not listed")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 1}, "0")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 2}, "1-2")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 3}, "2-4")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 4}, "5+")
    redcap_df = redcap_df.replace({'hba1c': 1}, "7.5-8.0")
    redcap_df = redcap_df.replace({'hba1c': 2}, "8.1-8.9")
    redcap_df = redcap_df.replace({'hba1c': 3}, "9.0-9.9")
    redcap_df = redcap_df.replace({'hba1c': 4}, "10+")
    #TODO Confirm this AGAIN - No. of self-reported physicians,	num_physicians,	int (1=1, 2=2-3, 4=4+)
    # Why do we skip 3? I assumed this was a mistake in the excel
    redcap_df = redcap_df.replace({'num_physicians': 1}, "1")
    redcap_df = redcap_df.replace({'num_physicians': 2}, "2-3")
    redcap_df = redcap_df.replace({'num_physicians': 2}, "2-3")
    redcap_df = redcap_df.replace({'num_rx': 1}, "1")
    redcap_df = redcap_df.replace({'num_rx': 2}, "2-4")
    redcap_df = redcap_df.replace({'num_rx': 3}, "5-9")
    redcap_df = redcap_df.replace({'num_rx': 4}, "10+")
    redcap_df = redcap_df.replace({'automaticity': 0}, "0")
    redcap_df = redcap_df.replace({'automaticity': 1}, "1")
    redcap_df = redcap_df.replace({'automaticity': 2}, "2-3")
    redcap_df = redcap_df.replace({'automaticity': 3}, "4")
    redcap_df = redcap_df.replace({'pt_activation': 1}, "yes")
    redcap_df = redcap_df.replace({'pt_activation': 2}, "most")
    redcap_df = redcap_df.replace({'pt_activation': 3}, "no")
    redcap_df = redcap_df.replace({'reason_dm_rx': 1}, "Supposed to")
    redcap_df = redcap_df.replace({'reason_dm_rx': 2}, "Own good")
    redcap_df = redcap_df.replace({'reason_dm_rx': 3}, "No choice")
    redcap_df = redcap_df.replace({'reason_dm_rx': 4}, "Feel good")
    redcap_df = redcap_df.replace({'reason_dm_rx': 5}, "Important")
    redcap_df = redcap_df.replace({'non_adherence': 0}, "0")
    redcap_df = redcap_df.replace({'non_adherence': 1}, "1")
    redcap_df = redcap_df.replace({'non_adherence': 2}, "2-3")
    redcap_df = redcap_df.replace({'non_adherence': 3}, "4-6")
    redcap_df = redcap_df.replace({'non_adherence': 4}, "7+")
    redcap_df = redcap_df.replace({'edu_level': 1}, "HS or below/HS grad")
    redcap_df = redcap_df.replace({'edu_level': 2}, "Some college")
    redcap_df = redcap_df.replace({'edu_level': 3}, "College grad/Postgrad")
    redcap_df = redcap_df.replace({'edu_level': 4}, "other")
    redcap_df = redcap_df.replace({'employment_status': 1}, "Employed")
    redcap_df = redcap_df.replace({'employment_status': 2}, "Retired/Other")
    redcap_df = redcap_df.replace({'marital_status': 1}, "Married/partner")
    redcap_df = redcap_df.replace({'marital_status': 2}, "window/divorced/single/other")
    return redcap_df
