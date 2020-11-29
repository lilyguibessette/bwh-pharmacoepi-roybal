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
from patient_data import get_study_ids

# For date time
#https://realpython.com/python-datetime/

def import_pt_data_control(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    # Imports Pillsy pill taking history as a pandas data frame from a CSV

    pt_data_filename = str(import_date) + "_pt_data_control" + '.csv'
    fp = os.path.join("..", "PatientDataControl", pt_data_filename)
    date_cols = ["start_date"]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    except FileNotFoundError:
        return None
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
    fp = os.path.join("..", "..", "PillsyControl", pillsy_filename)

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
        import re
        tz_abbr = re.search(r"\d\d:\d\d .M ([A-Z]{2,4}) \d{4}-\d\d-\d\d", time_string).group(1)
        return time_string.replace(tz_abbr, tz_ref[tz_abbr])

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
        drug_subset = timeframe_pillsy_subset[timeframe_pillsy_subset['drugName'] == drug].copy()
        this_drug_adherence = find_taken_events(drug, drug_subset)
        yesterday_adherence_by_drug.append(this_drug_adherence)

    sum_yesterday_adherence = sum(yesterday_adherence_by_drug)
    if sum_yesterday_adherence > 0:
        return True
    else:
        return False


def find_patient_rewards_control(patient, pillsy_subset, run_time):
    three_day_ago = (run_time - timedelta(days=3)).date()
    three_day_ago_12am = pytz.UTC.localize(datetime.combine(three_day_ago, datetime.min.time()))
    two_day_ago = (run_time - timedelta(days=2)).date()
    two_day_ago_12am = pytz.UTC.localize(datetime.combine(two_day_ago, datetime.min.time()))
    yesterday = (run_time - timedelta(days=1)).date()
    yesterday_12am = pytz.UTC.localize(datetime.combine(yesterday, datetime.min.time()))
    today_current_time = run_time
        # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
    today_12am = pytz.UTC.localize(datetime.combine(today_current_time, datetime.min.time()))

    pillsy_three_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < two_day_ago_12am].copy()
    pillsy_three_day_ago_subset = pillsy_three_day_ago_subset[pillsy_three_day_ago_subset["eventTime"] >= three_day_ago_12am].copy()

    pillsy_two_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < yesterday_12am].copy()
    pillsy_two_day_ago_subset = pillsy_two_day_ago_subset[pillsy_two_day_ago_subset["eventTime"] >= two_day_ago_12am].copy()

    pillsy_yesterday_subset = pillsy_subset[pillsy_subset["eventTime"] < today_12am].copy()
    pillsy_yesterday_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday].copy()

    pillsy_early_today_subset = pillsy_subset[pillsy_subset["eventTime"] >= today_12am].copy()
    pillsy_early_today_subset = pillsy_early_today_subset[pillsy_early_today_subset["eventTime"] < today_current_time].copy()


    taken_exists_t0 = check_for_any_taken_events(pillsy_yesterday_subset)
    taken_exists_t1 = check_for_any_taken_events(pillsy_two_day_ago_subset)
    taken_exists_t2 = check_for_any_taken_events(pillsy_three_day_ago_subset)
    early_rx_use = check_for_any_taken_events(pillsy_early_today_subset)


    if taken_exists_t0 or early_rx_use:
        patient["possibly_disconnected_day1"] = False
    elif taken_exists_t0 == False and early_rx_use == False:
        if patient["possibly_disconnected_day1"] == True:
            # Then we shift that indicator back a day and keep day1 disconnect true
            patient["possibly_disconnected_day2"] = True
            # We update the current variable that yes, today they were possibly_disconnected after 2 days
            # of 0 adherence / not in Pillsy data
            patient["possibly_disconnected"] = True
            # We increment the number of times this patient was flagged for possibly disconnected
            patient["num_possibly_disconnected_indicator_true"] += 1
            # We add yesterday's date to the possibly disconnected date and list of those dates as well
            patient["possibly_disconnected_date"] = yesterday
            patient["dates_possibly_disconnected"].append(yesterday)
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
    study_ids_list = get_study_ids(pt_data_control)
    for study_id in study_ids_list:
        patient = pt_data_control[pt_data_control["record_id"] == study_id]
        # Filter by firstname = study_id to get data for just this one patient
        patient_pillsy_subset = pillsy_control[pillsy_control["firstname"] == study_id]
        # This function will update the patient attributes with the updated adherence data that we will find from pillsy
        find_patient_rewards_control(patient, patient_pillsy_subset, run_time)

    #TODO ask joe how pandas df is manipulated in a function i.e. pass by val or ref?
    return


def write_disconnected_report(pt_data_control, run_time):
    disconnected_report_filename = str(run_time.date()) + "_disconnected_report_control" + '.csv'
    disconnected_report_filepath = os.path.join("..", "..", "DisconnectedHistoryControl", disconnected_report_filename)

    # Subset updated_pt_dict to what we need for reward calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['record_id', 'possibly_disconnected', 'trial_day_counter', 'censor_date']
    disconnected_report_df = pd.DataFrame(columns=column_values)

    for pt, data in pt_data_control.iterrows():
        # Reward value, Rank_Id's
        new_row = [data["record_id"], data["possibly_disconnected"], data["trial_day_counter"], str(data['censor_date'])]
        disconnected_report_df.loc[len(disconnected_report_df)] = new_row
    # Writes CSV for RA to send text messages.
    disconnected_report_df.to_csv(disconnected_report_filepath)
    return


def export_pt_data_control(pt_data_control, runtime):
    filesave = str(runtime.date()) + "_pt_data_control" + '.csv'
    filepath = os.path.join("..", "..", "PatientDataControl", filesave)
    pt_data_control.to_csv(filepath)

def check_control_disconnectedness(run_time):
    #TODO can i just make a new column by calling it and assigning it a value in a row? or nah?
    # @Joe - need help to think through for whole project where we instantiate a pt_data df cause rn its made on the fly
    pillsy_control = import_Pillsy_control(run_time)
    pt_data_control = import_pt_data_control(run_time)

    if pillsy_control and pt_data_control:
        find_disconnections_control(pt_data_control, pillsy_control, run_time)
        write_disconnected_report(pt_data_control) # assuming df operations are pass by ref? i.e. if we modified in find_rewards_control then
    else:
        fp = os.path.join("..", "PatientDataControl", "empty_start.csv")
        date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    redcap_control = import_redcap_control(run_time)
    redcap_study_ids = get_study_ids(redcap_control)
    study_ids_list = get_study_ids(pt_data_control)
    for id in redcap_study_ids:
        if id not in study_ids_list:
            redcap_row = redcap_control[redcap_control['record_id'] == id].iloc[0]
            censor_date = (redcap_row["start_date"] + timedelta(days=180)).date()
            new_row = pd.Series({'record_id': id,
                                         'trial_day_counter': 1,
                                         'start_date': redcap_row["start_date"],
                                         'censor_date': censor_date,
                                         'censor': redcap_row["censor"]}, name=id)
            pt_data_control = pt_data_control.append(new_row)
    export_pt_data_control(pt_data_control, run_time)
