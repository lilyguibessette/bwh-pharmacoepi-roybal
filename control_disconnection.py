import pandas as pd
import numpy as np
import sys
import os
import re
import gc
import time
from datetime import datetime, date, timedelta
import pytz
from pillsy_parser import identify_drug_freq, find_patient_rewards, get_drugName_list, find_taken_events, find_rewards
from patient_data import get_study_ids, new_empty_pt_data

# For date time
#https://realpython.com/python-datetime/

def import_pt_data_control(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
 
    pt_data_filename = str(import_date) + "_pt_data_control" + '.csv'
    fp = os.path.join("..", "PatientDataControl", pt_data_filename)
    date_cols = ["start_date", "censor_date"]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols) #, dtype=data_types)
    except FileNotFoundError as fnfe:
        print("in patient_data.py, in import_pt_data")
        print("fp file not found, fp = {}".format(os.path.abspath(fp)))
        print("error = {}".format(fnfe))
        pt_data = new_empty_pt_data()
        return pt_data
    return pt_data

def import_redcap_control(run_time):
    import_date = run_time.date()
    # Imports REDCap patients that are enrolling on an ongoing basis as a pandas data frame from a CSV
    redcap_filepath = str(import_date) + "_redcap_control" + '.csv'
    fp = os.path.join("..", "REDCapControl", redcap_filepath)
    date_cols = ["start_date"]
    # Reads in the csv file into a pandas data frame and ensures that the date_cols are imported as datetime.datetime objects
    # TODO potentially need to be careful here due to use of the data in redcap.py -> might want to ensure record_id column is a string, currently I think it defaults to an int - might bee fine to keep int
    redcap = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    # Returns the pandas dataframe of REDCap patient data that is read in
    # Note: The REDCap data does not contain observed feedback.
    # Hence why we do not overwrite our previous patient dictionary based on this data.
    # This is used to update patient dictionary data about:
    #   -   Whether patients are censored (i.e. due to death, consent withdrawal,
    #   -   Changes in Pillsy medications that a patient is taking
    #   -   Add entirely new patients initiating in the study to our patient dictionary by creating new patient objects
    return redcap

def import_Pillsy_control(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    # Imports Pillsy pill taking history as a pandas data frame from a CSV

    pillsy_filename = str(import_date) + "_pillsy_control" + '.csv'
    fp = os.path.join("..", "PillsyControl", pillsy_filename)

    try:
        pillsy = pd.read_csv(fp)
    except FileNotFoundError:
        fp = os.path.join("..", "PillsyControl", "empty_pillsy_start.csv")
        pillsy = pd.read_csv(fp)
        return pillsy

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
        import re
        tz_abbr = re.search(r"\d\d:\d\d .M ([A-Z]{2,4}) \d{4}-\d\d-\d\d", time_string).group(1)
        return time_string.replace(tz_abbr, tz_ref[tz_abbr])

    pillsy.dropna(
    axis=0,
    how='all',
    thresh=None,
    subset=None,
    inplace=True)
    #https://hackersandslackers.com/pandas-dataframe-drop/
    
    #TODO: Here we need to drop the empty rows.
    pillsy["eventTime"] = pd.to_datetime(pd.Series([converter(str_dt) for str_dt in pillsy["eventTime"]])) #, utc=True)
    # Note: In this dataset our study_id is actually 'firstname', hence the drop of patientId
    # Note: firstname is currently read in as int64 dtype
    pillsy.drop(["patientId", "lastname", "method", "platform"], axis=1, inplace=True)
    return pillsy


def find_disconnections_control(pt_data_control, pillsy_control, run_time):
    """
    find_rewards function iteratees through the patients in pt_data to update their adherence measurements
    (daily and cumulative) and thereby reward values; also updates diconnectedness and early_rx_use features
    :param pillsy:
    :param pillsy_study_ids_list:
    :param pt_data:
    :param run_time:
    :return:
    """
    control_pt_data = new_empty_pt_data()
    study_ids_list = get_study_ids(pt_data_control)
    for study_id in study_ids_list:
        patient = pt_data_control[pt_data_control["record_id"] == study_id].iloc[0]
        # Filter by firstname = study_id to get data for just this one patient
        patient_pillsy_subset = pillsy_control[pillsy_control["firstname"] == study_id]
        # This function will update the patient attributes with the updated adherence data that we will find from pillsy
        patient = find_patient_rewards_control(patient, patient_pillsy_subset, run_time)
        control_pt_data = control_pt_data.append(patient)
    #TODO ask joe how pandas df is manipulated in a function i.e. pass by val or ref?
    return control_pt_data


def export_pt_data_control(pt_data_control, runtime):
    filesave = str(runtime.date()) + "_pt_data_control" + '.csv'
    filepath = os.path.join("..", "PatientDataControl", filesave)
    pt_data_control.to_csv(filepath, index=False)

def check_control_disconnectedness(run_time, pillsy, pt_data_control, redcap_control):
    #TODO can i just make a new column by calling it and assigning it a value in a row? or nah?
    # @Joe - need help to think through for whole project where we instantiate a pt_data df cause rn its made on the fly
    
    if not pillsy.empty and not pt_data_control.empty:
        pt_data_control = find_rewards(pillsy, pt_data_control, run_time)
    
    pt_data_control = update_pt_data_with_redcap(redcap_data, pt_data, run_time)
    
    ranked_pt_data = new_empty_pt_data()
    for index, patient in pt_data_control.iterrows():
        if patient["censor"] != 1 and patient["censor_date"] > run_time.date():
            patient = run_ranking(patient, client, run_time)
            ranked_pt_data = ranked_pt_data.append(patient)
            
    redcap_study_ids = get_study_ids(redcap_control)
    study_ids_list = get_study_ids(pt_data_control)
    for id in redcap_study_ids:
        if id not in study_ids_list:
            redcap_row = redcap_control[redcap_control['record_id'] == id].iloc[0]
            if redcap_row['censor'] == 1:
                continue
            censor_date = (redcap_row["start_date"] + timedelta(days=180)).date()
            new_row = pd.Series({'record_id': id,
                                 'trial_day_counter': 1,
                                 'start_date': redcap_row["start_date"],
                                 'censor_date': censor_date,
                                 'censor': redcap_row["censor"],
                                 'disconnectedness':False,
                                 'num_dates_disconnectedness': 0,
                                 'num_dates_early_rx_use': 0,
                                 'num_pillsy_meds_t0': redcap_row["bottles"]}, name=id)
            pt_data_control = pt_data_control.append(new_row)
    export_pt_data_control(pt_data_control, run_time)
