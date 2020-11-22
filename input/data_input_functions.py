import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil import parser, tz
import pickle
import os
import re

def import_Pillsy(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    # Imports Pillsy pill taking history as a pandas data frame from a CSV

    pillsy_filename = str(import_date) + "_pillsy" + '.csv'
    fp = os.path.join("..", "..", "Pillsy", pillsy_filename)

    try:
    	pillsy = pd.read_csv(fp)
    except FileNotFoundError:
    	return None
    
    tz_ref = {
    	"HDT": "-0900", 
    	"HST": "-1000",
    	"AKDT": "-0800", 
    	"AKST": "-0900",
    	"PDT": "-0700", 
    	"PST": "-0800",
    	"MDT": "-0600", 
    	"MST": "-0700",
    	"CDT": "-0500", 
    	"CST": "-0600",
    	"EDT": "-0400", 
    	"EST": "-0500"
    }
    def converter(time_string):
    	tz_abbr = re.search(r"\d\d:\d\d A|PM ([A-Z]{2,4}) \d{4}-\d\d-\d\d", time_string).group(1)
    	return time_string.replace(tz_abbr, tz_ref[tz_abbr])
    pillsy["eventTime"] = pd.to_datetime(pillsy["eventTime"])
	# Note: In this dataset our study_id is actually 'firstname', hence the drop of patientId
	# Note: firstname is currently read in as int64 dtype
    pillsy.drop(["patientId", "lastname", "method", "platform"], axis=1, inplace=True)
    return pillsy

def import_redcap(run_time):
    import_date = run_time.date()
    # Imports REDCap patients that are enrolling on an ongoing basis as a pandas data frame from a CSV
    redcap_filepath = str(import_date) + "_redcap" + '.csv'
    fp = os.path.join("..", "..", "..", "REDCap", redcap_filepath)
    date_cols = ["start_date"]
    # Reads in the csv file into a pandas data frame and ensures that the date_cols are imported as datetime.datetime objects
    # TODO potentially need to be careful here due to use of the data in redcap.py -> might want to ensure record_id column is a string, currently I think it defaults to an int
    redcap = pd.read_csv(fp, sep=',', parse_dates=date_cols)

    # Returns the pandas dataframe of REDCap patient data that is read in
    # Note: The REDCap data does not contain observed feedback.
    # Hence why we do not overwrite our previous patient dictionary based on this data.
    # This is used to update patient dictionary data about:
    #   -   Whether patients are censored (i.e. due to death, consent withdrawal,
    #   -   Changes in Pillsy medications that a patient is taking
    #   -   Add entirely new patients initiating in the study to our patient dictionary by creating new patient objects
    return redcap

def load_dict_pickle(run_time):
    try:
        # At the start of the program we will try to open the patient dictionary pickle from yesterday to use for today
        # This patient dictionary is used to represent the current patient data that we have at the start of the program
        #   - i.e. before update with Pillsy with yesterday's adherence data for reward calls /
        #          what would be used for today's rank call
        import_date = (run_time - pd.Timedelta("1 day")).date()
        pickle_filename = str(import_date) + "_patient_dict" + '.pickle'
        fp = os.path.join("..", "..", "PatientData", pickle_filename)
        with open(fp, 'rb') as pfile:
            pickle_dict = pickle.load(pfile)
    except:
        # If we try to open the patient dictionary pickle and it is unable to/doesn't exists,
        # then we instantiate an empty dictionary to be used.
        # - i.e. at study initiation where no patients have been enrolled
        pickle_dict = {}
    # Returns the patient dictionary imported from the pickle
    # This is a dictionary where keys are study_id's of patients and the values are Patient class objects.
    return pickle_dict
