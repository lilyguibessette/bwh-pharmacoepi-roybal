import pandas as pd
import numpy as np
import sys
import os
import re
import gc
import time
from datetime import datetime, date, timedelta
import pytz
from fresh_restart.patient_data import get_study_ids

# For date time
#https://realpython.com/python-datetime/



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
        import re
        tz_abbr = re.search(r"\d\d:\d\d A|PM ([A-Z]{2,4}) \d{4}-\d\d-\d\d", time_string).group(1)
        return time_string.replace(tz_abbr, tz_ref[tz_abbr])

    pillsy["eventTime"] = pd.to_datetime(converter(pillsy["eventTime"]))
    # Note: In this dataset our study_id is actually 'firstname', hence the drop of patientId
    # Note: firstname is currently read in as int64 dtype
    pillsy.drop(["patientId", "lastname", "method", "platform"], axis=1, inplace=True)
    return pillsy


def get_drugName_list(patient_entries):
    try:
        drugNames_df = patient_entries['drugName']
        unique_drugNames_df = drugNames_df.drop_duplicates()
        unique_drugNames_df_list = unique_drugNames_df.values.tolist()
    except ValueError:
        unique_drugNames_df_list = []
    return unique_drugNames_df_list



def identify_drug_freq(drugName):
    """
    identify_drug_freq function checks the drugName for QD or BID to return either 1 or 2
    as the underlying expected number of taken events
    :param drugName:
    :return: drugFreq
    """
    drugFreq = 0
    # drugName is a String
    # .find returns -1 if it doesn't find the String QD or BID in the drugName String
    # If the drugName does contain QD or BID, then .find() will return an int > -1 (0 or more)
    # at the index of the first occurrence of the BID or QD string
    if drugName.find('QD') > -1:
        drugFreq = 1
    elif drugName.find('BID') > -1:
        drugFreq = 2
    # Returns the number of doses that the given Medication is
    return drugFreq

# def update_pt_dict(pt_dict_with_reward, pt_dict_without_reward):
#     updated_pt_dict = {**pt_dict_with_reward, **pt_dict_without_reward}
#     return updated_pt_dict

def find_taken_events(drug, drug_subset):
    """
    find_taken_events function finds the adherence for a particular drug when run over a particular time period using
    the investigator specified algorithm for evaluating OPEN/CLOSE sequences as taken events
    :param drug:
    :param drug_subset:
    :return:
    """
    fifteen_min = pd.Timedelta('15 minutes')
    two_hr_45_min = pd.Timedelta('2 hours, 45 minutes')
    drug_freq = identify_drug_freq(drug)
    taken = 0
    drug_adherence = 0
    taken_events = []
    first_taken = None
    maybe_taken_event = None
    for index, row in drug_subset.iterrows():
        if drug_freq == taken:
            break
        if row['eventValue'] == "OPEN" and not taken_events:
            first_taken = row['eventTime']
            taken_events.append(first_taken)
            taken += 1
        elif row['eventValue'] == "CLOSE" and not taken_events:
            maybe_taken_event = row['eventTime']
        elif maybe_taken_event:
            diff = row['eventTime'] - maybe_taken_event
            if diff < fifteen_min:
                taken_events.append(maybe_taken_event + fifteen_min)
                taken += 1
    if drug_freq != taken and first_taken:
        find_second_taken_subset = drug_subset[drug_subset["eventTime"] >= first_taken].copy()
        for index, second_pass in find_second_taken_subset.iterrows():
            if drug_freq == taken:
                break
            diff_second = second_pass['eventTime'] - first_taken
            if diff_second > two_hr_45_min:
                taken_events.append(second_pass['eventTime'])
                taken += 1
    if drug_freq > 0:
        drug_adherence = taken / drug_freq
    return drug_adherence

def compute_taken_over_expected(patient, timeframe_pillsy_subset):
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
    taken_over_expected = 0
    if patient:
        sum_yesterday_adherence = sum(yesterday_adherence_by_drug)
        taken_over_expected = sum_yesterday_adherence / patient["num_pillsy_meds"]
    else:
        taken_over_expected = 0
    return taken_over_expected


def shift_day_adherences(patient, reward_value_t0):
    """
    shift_day_adherences function to shift the values of each column over by one day
    :param patient:
    :param reward_value_t0:
    :return:
    """
    patient["adherence_day7"] = patient["adherence_day6"]
    patient["adherence_day6"] = patient["adherence_day5"]
    patient["adherence_day5"] = patient["adherence_day4"]
    patient["adherence_day4"] = patient["adherence_day3"]
    patient["adherence_day3"] = patient["adherence_day2"]
    patient["adherence_day2"] = patient["adherence_day1"]
    patient["adherence_day1"] = reward_value_t0

def shift_dichot_day_adherences(patient, reward_value_t0):
    """
    shift_dichot_day_adherences function to shift the values of each column over by one day
    :param patient:
    :param reward_value_t0:
    :return:
    """
    patient["dichot_adherence_day7"] = patient["dichot_adherence_day6"]
    patient["dichot_adherence_day6"] = patient["dichot_adherence_day5"]
    patient["dichot_adherence_day5"] = patient["dichot_adherence_day4"]
    patient["dichot_adherence_day4"] = patient["dichot_adherence_day3"]
    patient["dichot_adherence_day3"] = patient["dichot_adherence_day2"]
    patient["dichot_adherence_day2"] = patient["dichot_adherence_day1"]
    if reward_value_t0 > 0:
        patient["dichot_adherence_day1"] = 1
    else:
        patient["dichot_adherence_day1"] = 0

def update_day2_adherence(patient, reward_value_t1):
    """
    update_day2_adherence function to reassign the value from two days ago in case of updated sync'd/reconnected data
    :param patient:
    :param reward_value_t1:
    :return:
    """
    patient["adherence_day2"] = reward_value_t1

def update_day2_dichot_adherence(patient,reward_value_t1):
    """
    update_day2_dichot_adherence function to reassign the value from two days ago in case of updated sync'd/reconnected data
    :param patient:
    :param reward_value_t1:
    :return:
    """
    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
    if reward_value_t1 > 0:
        patient["dichot_adherence_day2"] = 1
    else:
        patient["dichot_adherence_day2"] = 0


def update_day3_adherence(patient, reward_value_t2):
    """
    update_day2_adherence function to reassign the value from two days ago in case of updated sync'd/reconnected data
    :param patient:
    :param reward_value_t1:
    :return:
    """
    patient["adherence_day3"] = reward_value_t2

def update_day3_dichot_adherence(patient,reward_value_t2):
    """
    update_day2_dichot_adherence function to reassign the value from two days ago in case of updated sync'd/reconnected data
    :param patient:
    :param reward_value_t1:
    :return:
    """
    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
    if reward_value_t2 > 0:
        patient["dichot_adherence_day3"] = 1
    else:
        patient["dichot_adherence_day3"] = 0

def calc_avg_adherence(patient):
    """
    calc_avg_adherence function updates the avg adherences at days 1,3,7 with updated shifted daily adherence values
    :param patient:
    :return:
    """
    if patient["trial_day_counter"] < 3:
        patient["avg_adherence_1day"] = patient["adherence_day1"]
    elif 3 <= patient["trial_day_counter"] < 7:
        patient["avg_adherence_3day"] = (patient["adherence_day1"] + patient["adherence_day2"] + patient["adherence_day3"]) / 3
        patient["avg_adherence_1day"] = patient["adherence_day1"]
    elif patient["trial_day_counter"] >= 7:
        patient["avg_adherence_7day"] = (
                                          patient["adherence_day1"] + patient["adherence_day2"] + patient["adherence_day3"] + patient["adherence_day4"] + patient["adherence_day5"] + patient["adherence_day6"] + patient["adherence_day7"]) / 7
        patient["avg_adherence_3day"] = (patient["adherence_day1"] + patient["adherence_day2"] + patient["adherence_day3"]) / 3
        patient["avg_adherence_1day"] = patient["adherence_day1"]

def find_patient_rewards(pillsy_subset, patient, run_time):
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

    # Use calendar day of yesterday to compute adherence
    reward_value_t0 = compute_taken_over_expected(patient, pillsy_yesterday_subset)

    # if early_today_rx_use = 1 from last run then we don't need this measurement because
    # then two runs ago was truly 0 and we should still find 0 so might as well run again
    # Use calendar day of two days ago to update the reward if we suspected a disconnection
    reward_value_t1 = compute_taken_over_expected(patient, pillsy_two_day_ago_subset)
    # if disconnectedness was -1 last time, then we need to send this updated reward_value_t1
    # regardless of what it is now (i.e. we will send 0's or the updated adherence if they reconnected

    reward_value_t2 = compute_taken_over_expected(patient, pillsy_three_day_ago_subset)


    early_rx_use = compute_taken_over_expected(patient, pillsy_early_today_subset)


    # Check if two reward assessments ago we were unsure about disconnectedness

    if patient["possibly_disconnected"] == True:
        patient["flag_send_reward_value_t2"] = True
    else:
        patient["flag_send_reward_value_t2"] = False

    if patient["disconnectedness"] == -1:
        if reward_value_t1 != patient["reward_value_t0"]:
            patient["flag_send_reward_value_t1"] = True
        else:
            patient["flag_send_reward_value_t1"] = False



    # Update data frame with new values for reward and
    patient["reward_value_t0"] = reward_value_t0
    patient["reward_value_t1"] = reward_value_t1
    patient["reward_value_t2"] = reward_value_t2
    patient["early_rx_use"] = early_rx_use

    # Shifts the adherence for each day backwards by 1 day to make day1 = newest found avg_adherence
    # and day2 = old day, day3 = old day 2... etc day7 = old day 6
    shift_day_adherences(patient, reward_value_t0)
        #function to shift the values of each column over by one day
    shift_dichot_day_adherences(patient, reward_value_t0)
        #function to shift the values of each column over by one day
    update_day2_adherence(patient, reward_value_t1)
        #function to reassign the value from two days ago in case updated sync'd data
    update_day2_dichot_adherence(patient, reward_value_t1)
        #function to reassign the value from two days ago in case updated sync'd data
    update_day3_adherence(patient, reward_value_t2)
    # function to reassign the value from two days ago in case updated sync'd data
    update_day3_dichot_adherence(patient, reward_value_t2)
    # function to reassign the value from two days ago in case updated sync'd data

    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
    calc_avg_adherence(patient)

    if reward_value_t0 > 0 and early_rx_use == 0:
        patient["flag_send_reward_value_t0"] = True
        patient["disconnectedness"] = 1
    elif reward_value_t0 > 0 and early_rx_use == 1:
        patient["flag_send_reward_value_t0"] = True
        patient["disconnectedness"] = 0
    elif reward_value_t0 == 0 and early_rx_use == 0:
        patient["flag_send_reward_value_t0"] = False
        patient["disconnectedness"] = -1
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

    return patient # this function can either return the updated row of data
    # or just update in place but dont know how dataframes work for pass by ref vs pass by val

def find_rewards(pillsy, pt_data, run_time):
    """
    find_rewards function iteratees through the patients in pt_data to update their adherence measurements
    (daily and cumulative) and thereby reward values; also updates diconnectedness and early_rx_use features
    :param pillsy:
    :param pillsy_study_ids_list:
    :param pt_data:
    :param run_time:
    :return:
    """
    study_ids_list = get_study_ids(pt_data)
    for study_id in study_ids_list:
        # Filter by firstname = study_id to get data for just this one patient
        patient_pillsy_subset = pillsy[pillsy["firstname"] == study_id]
        patient_row = pt_data[pt_data["record_id"] == study_id]
        # This function will update the patient attributes with the updated adherence data that we will find from pillsy
        find_patient_rewards(patient_pillsy_subset, patient_row, run_time)

    #TODO ask joe how pandas df is manipulated in a function i.e. pass by val or ref?
    return


