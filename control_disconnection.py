import pandas as pd
import numpy as np
import sys
import os
import re
import gc
import time
from datetime import datetime, date, timedelta
import pytz
from pillsy_parser import identify_drug_freq, get_drugName_list, find_taken_events
from patient_data import get_study_ids, new_empty_pt_data

# For date time
#https://realpython.com/python-datetime/

def import_pt_data_control(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
 
    pt_data_filename = str(import_date) + "_pt_data_control" + '.csv'
    fp = os.path.join("..", "PatientDataControl", pt_data_filename)
    date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    except FileNotFoundError:
        fp = os.path.join("..", "PatientDataControl", "empty_start.csv")
        date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
        pt_data_control = pd.read_csv(fp, sep=',', parse_dates=date_cols)
        return pt_data_control
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
    pillsy["eventTime"] = pd.to_datetime(pd.Series([converter(str_dt) for str_dt in pillsy["eventTime"]]))
    # Note: In this dataset our study_id is actually 'firstname', hence the drop of patientId
    # Note: firstname is currently read in as int64 dtype
    pillsy.drop(["patientId", "lastname", "method", "platform"], axis=1, inplace=True)
    return pillsy

def check_for_any_taken_events(timeframe_pillsy_subset):
    """
    compute_taken_over_expected function runs find_taken_events for each drug to find the adherence of each drug
    over a given time frame and then computes the average adherence for the time period by dividing the sum of
    adherence of all drugs over the number of drugs (i.e. expected maximum sum of adherence) for a patient
    :param patient:
    :param timeframe_pillsy_subset:
    :return:
    """
    yesterday_drugs = get_drugName_list(timeframe_pillsy_subset)
    yesterday_adherence_by_drug = [0] * len(yesterday_drugs)
    drug_num = 0
    for drug in yesterday_drugs:
        drug_num += 1
        drug_subset = timeframe_pillsy_subset[timeframe_pillsy_subset['drugName'] == drug]
        this_drug_adherence = find_taken_events(drug, drug_subset)
        yesterday_adherence_by_drug.append(this_drug_adherence)

    sum_yesterday_adherence = sum(yesterday_adherence_by_drug)
    if sum_yesterday_adherence > 0:
        return True
    else:
        return False


def find_patient_rewards_control(patient, pillsy_subset, run_time):
    # From pillsy_subset, get timezone of patient, then use that to calculate the time cut points so that it is relative to the
    # patient's view of time.
    curtime = run_time
    tzinfo_first_row = run_time.tzinfo
    first_row = pillsy_subset.head(1)
    if not first_row.empty:
        print(first_row['eventTime'].values[0])
        tzinfo_first_row = first_row['eventTime'].values[0].tzinfo
        curtime = curtime.astimezone(tzinfo_first_row)

    three_day_ago = (curtime - timedelta(days=3)).date()
    three_day_ago_12am = datetime.combine(three_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)
    two_day_ago = (curtime - timedelta(days=2)).date()
    two_day_ago_12am = datetime.combine(two_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)
    yesterday = (curtime - timedelta(days=1)).date()
    yesterday_12am =datetime.combine(yesterday, datetime.min.time()).astimezone(tzinfo_first_row)
    today_current_time = curtime
        # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
    today_12am = datetime.combine(today_current_time, datetime.min.time()).astimezone(tzinfo_first_row)

    pillsy_three_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < two_day_ago_12am]
    pillsy_three_day_ago_subset = pillsy_three_day_ago_subset[pillsy_three_day_ago_subset["eventTime"] >= three_day_ago_12am]

    pillsy_two_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < yesterday_12am]
    pillsy_two_day_ago_subset = pillsy_two_day_ago_subset[pillsy_two_day_ago_subset["eventTime"] >= two_day_ago_12am]

    pillsy_yesterday_subset = pillsy_subset[pillsy_subset["eventTime"] < today_12am]
    pillsy_yesterday_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday_12am]

    pillsy_early_today_subset = pillsy_subset[pillsy_subset["eventTime"] >= today_12am]
    pillsy_early_today_subset = pillsy_early_today_subset[pillsy_early_today_subset["eventTime"] < today_current_time]

    pillsy_yesterday_disconnectedness_subset = pillsy_subset[pillsy_subset["eventTime"] < today_current_time]
    pillsy_yesterday_disconnectedness_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday_12am]

    taken_exists_t0 = check_for_any_taken_events(pillsy_yesterday_subset)
    taken_exists_t1 = check_for_any_taken_events(pillsy_two_day_ago_subset)
    taken_exists_t2 = check_for_any_taken_events(pillsy_three_day_ago_subset)
    early_rx_use = check_for_any_taken_events(pillsy_early_today_subset)

    
    observed_num_drugs = get_drugName_list(pillsy_yesterday_disconnectedness_subset)
    if len(observed_num_drugs) == patient["num_pillsy_meds_t0"]:
        yesterday_disconnectedness = 1
    else:
        yesterday_disconnectedness = -1        
    
        
    if early_rx_use > 0:
        patient["num_dates_early_rx_use"] += 1
        
    if yesterday_disconnectedness == 1:
        patient["possibly_disconnected_day1"] = False
    elif yesterday_disconnectedness == -1:
        patient["disconnectedness"] = -1
        patient["num_dates_disconnectedness"] += 1
        if patient["possibly_disconnected_day1"] == True:
            # Then we shift that indicator back a day and keep day1 disconnect true
            patient["possibly_disconnected_day2"] = True
            # We update the current variable that yes, today they were possibly_disconnected after 2 days
            # of 0 adherence / not in Pillsy data
            patient["possibly_disconnected"] = True
            # We increment the number of times this patient was flagged for possibly disconnected
            patient["num_dates_possibly_disconnected"] += 1
            # We add yesterday's date to the possibly disconnected date 
            patient["possibly_disconnected_date"] = yesterday
            #patient["dates_possibly_disconnected"].append(yesterday)
        else:
            patient["possibly_disconnected_day1"] = True
            patient["possibly_disconnected_day2"] = False
    patient['trial_day_counter'] += 1
    return patient # this function can either return the updated row of data
    # or just update in place but dont know how dataframes work for pass by ref vs pass by val

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


def write_disconnected_report(pt_data_control, run_time):
    disconnected_report_filename = str(run_time.date()) + "_disconnected_report_control" + '.csv'
    disconnected_report_filepath = os.path.join("..",  "DisconnectedHistoryControl", disconnected_report_filename)

    # Subset updated_pt_dict to what we need for reward calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['record_id','disconnectedness','num_dates_disconnectedness', 'possibly_disconnected', 'num_dates_possibly_disconnected','early_rx_use','num_dates_early_rx_use', 'trial_day_counter', 'censor_date']
    disconnected_report_df = pd.DataFrame(columns=column_values)

    for pt, data in pt_data_control.iterrows():
        # Reward value, Rank_Id's
        new_row = [data["record_id"], data["disconnectedness"],data["num_dates_disconnectedness"],  data["possibly_disconnected"], 
                   data["num_dates_possibly_disconnected"], data["early_rx_use"], data["num_dates_early_rx_use"], data["trial_day_counter"], str(data['censor_date'])]
        disconnected_report_df.loc[len(disconnected_report_df)] = new_row
    # Writes CSV for RA to send text messages.
    disconnected_report_df.to_csv(disconnected_report_filepath)
    return


def export_pt_data_control(pt_data_control, runtime):
    filesave = str(runtime.date()) + "_pt_data_control" + '.csv'
    filepath = os.path.join("..", "PatientDataControl", filesave)
    pt_data_control.to_csv(filepath, index=False)

def check_control_disconnectedness(run_time):
    #TODO can i just make a new column by calling it and assigning it a value in a row? or nah?
    # @Joe - need help to think through for whole project where we instantiate a pt_data df cause rn its made on the fly
    pillsy_control = import_Pillsy_control(run_time)
    pt_data_control = import_pt_data_control(run_time)

    if not pillsy_control.empty and not pt_data_control.empty:
        pt_data_control = find_disconnections_control(pt_data_control, pillsy_control, run_time)
        write_disconnected_report(pt_data_control, run_time)
        
    redcap_control = import_redcap_control(run_time)
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
                                 'possibly_disconnected':False,
                                 'possibly_disconnected_day1':False,
                                 'possibly_disconnected_day2':False,
                                 'num_pillsy_meds_t0': redcap_row["bottles"],
                                 'num_pillsy_meds_t1': redcap_row["bottles"],
                                 'num_pillsy_meds_t2': redcap_row["bottles"]}, name=id)
            pt_data_control = pt_data_control.append(new_row)
    export_pt_data_control(pt_data_control, run_time)
