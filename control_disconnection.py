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
from exe_functions import build_path
from driverRank import shift_t0_t1_rank_ids
from redcap_parser import update_pt_data_with_redcap

# For date time
#https://realpython.com/python-datetime/

def import_pt_data_control(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    fp = build_path("000_PatientDataControl", str(import_date) + "_pt_data_control.csv")
    date_cols = ["start_date", "censor_date"]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    except FileNotFoundError as fnfe:
        while True:
            first_day = input("\nIs today the trial initiation?\n" 
                      + "If today is the first day, type 'yes' then hit Enter.\n"
                      + "Otherwise type 'no' then hit Enter.\n"
                      + "Answer here: ").lower()
            if first_day in ["yes", "no"]:
                first_day = first_day == "yes"
                break
            else:
                print("Input was not 'yes' or 'no'. Please try again.")
        if not first_day:
            input("\n" + str(import_date) + "_pt_data_control.csv not found in the 000_PatientDataControl folder.\n"
                  + "This file should always exist with yesterday's date in the name. Please contact Lily.\n"
                  + "Press Enter to exit the program and close this window.")
            sys.exit()
        pt_data = new_empty_pt_data()
        return pt_data
    return pt_data

def import_redcap_control(run_time):
    fp = build_path("000_REDCapControl", str(run_time.date()) + "_redcap_control.csv")
    date_cols = ["start_date"]
    try:
        redcap = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    except FileNotFoundError:
        input("\n" + str(run_time.date()) + "_redcap_control.csv was not found in the REDCapControl folder.\n"
              + "This should be today's date in YYYY-MM-DD format followed by _redcap_control.csv\n"
              + "and this must be placed in the 000_REDCapControl folder.\n"
              + "Please make sure this data has been downloaded and named properly.\n"
              + "Please run the program again after fixing the file name.\n"
              + "Press Enter to exit the program and close this window.")
        sys.exit()
    return redcap

def check_control_disconnectedness(pillsy, redcap_data, pt_data, run_time):
    #TODO can i just make a new column by calling it and assigning it a value in a row? or nah?
    # @Joe - need help to think through for whole project where we instantiate a pt_data df cause rn its made on the fly
    
    if not pt_data.empty and pillsy is not None:
        pt_data_control = find_rewards(pillsy, pt_data, run_time)
    
    pt_data_control = update_pt_data_with_redcap(redcap_data, pt_data_control, run_time)
    
    ranked_pt_data = new_empty_pt_data()
    for index, patient in pt_data_control.iterrows():
        if patient["censor"] != 1 and patient["censor_date"] > run_time.date():
            patient= shift_t0_t1_rank_ids(patient)
            patient["trial_day_counter"] += 1
            ranked_pt_data = ranked_pt_data.append(patient)
            
   
    ranked_pt_data.to_csv(build_path("000_PatientDataControl", str(run_time.date()) + "_pt_data_control.csv"),   index=False)
