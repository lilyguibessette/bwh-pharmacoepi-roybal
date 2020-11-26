import pandas as pd
import numpy as np
import sys
import os
import re
import gc
import time
from datetime import datetime, date, timedelta
import pytz

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

def get_pillsy_study_ids(pillsy):
    try:
    # Subsets the firstname column to find the unique study_id's available in the Pillsy data to update adherence
        study_ids_df = pillsy['firstname']
        unique_study_ids_df = study_ids_df.drop_duplicates()
        unique_study_ids_list = unique_study_ids_df.values.tolist()
    except ValueError:
        unique_study_ids_list = []
    return unique_study_ids_list

def identify_drug_freq(drugName):
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
    fifteen_min = pd.Timedelta('15 minutes')
    two_hr_45_min = pd.Timedelta('2 hours, 45 minutes')
    drug_freq = identify_drug_freq(drug)
    taken = 0
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
    drug_adherence = taken / drug_freq
    return drug_adherence


def compute_taken_over_expected(patient, timeframe_pillsy_subset):
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
    return taken_over_expected



def find_patient_rewards(pillsy_subset, patient, run_time):
    two_day_ago = (run_time - timedelta(days=2)).date()
    two_day_ago_12am = pytz.UTC.localize(datetime.combine(two_day_ago, datetime.min.time()))
    yesterday = (run_time - timedelta(days=1)).date()
    yesterday_12am = pytz.UTC.localize(datetime.combine(yesterday, datetime.min.time()))
    today_current_time = run_time
        # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
    today_12am = pytz.UTC.localize(datetime.combine(today_current_time, datetime.min.time()))

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

    early_rx_use = compute_taken_over_expected(patient, pillsy_early_today_subset)

    # Shifts the adherence for each day backwards by 1 day to make day1 = newest found avg_adherence
    # and day2 = old day, day3 = old day 2... etc day7 = old day 6
    shift_day_adherences(patient, reward_value_t0) #TODO function to shift the values of each column over by one day
    shift_dichot_day_adherences(patient, reward_value_t0) #TODO function to shift the values of each column over by one day

    update_day2_adherence(reward_value_t1) #TODO function to reassign the value from two days ago in case updated sync'd data
    update_day2_dichot_adherence(reward_value_t1) #TODO function to reassign the value from two days ago in case updated sync'd data
    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:

    calc_avg_adherence(patient) #TODO function that operates on the current row of data

    if reward_value_t0 > 0 and early_rx_use == 0:
        disconnectedness = 1
    elif reward_value_t0 > 0 and early_rx_use == 1:
        disconnectedness = 0
    elif reward_value_t0 == 0 and early_rx_use == 0:
        disconnectedness = -1
        if patient["possibly_disconnected_day1"] == True:
            # Then we shift that indicator back a day and keep day1 disconnect true
            possibly_disconnected_day2 = True
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

    return patient # this function can either return the updated row of data
    # or just update in place but dont know how dataframes work for pass by ref vs pass by val

def find_rewards(pillsy, pillsy_study_ids_list, pt_data, run_time):
    for study_id in pillsy_study_ids_list:
            # Filter by firstname = study_id to get data for just this one patient
        patient_pillsy_subset = pillsy[pillsy["firstname"] == study_id].copy()
            # Now we will send our current patient object to the find_patient_rewards function with their study_id & pillsy subset
        # switch to identifying the subset
        patient_rows = pt_data[pt_data["record_id"] == study_id]
            # This function with update the patient attributes with the updated adherence data that we will find from pillsy
        find_patient_rewards(patient_pillsy_subset, patient_rows, run_time)
            # The function returns an updated patient
            # We add this patient to our originally empty pt_dict_with_reward dictionary with their study_id as a key


        # Now that we've iterated through all patients in the Pillsy data, we identify the patients not found at all
        # Therefore these patients do not have any rewards to send to Personalizer, but we still need to update them and
        # shift their adherence and also add indicators that they may be disconnected.
        pt_dict_without_reward = {}

        # Store Yesterday's date if we need to record that as the date they've been marked as disconnected (i.e. 2 days without Pillsy info)
        yesterday = (run_time - timedelta(days=1)).date()
        for pt, pt_data_to_update in pt_data.items():
            # If patient was not in Pillsy data,
            if pt not in pillsy_study_ids_list:
                # Then update their adherence by shifting over a day
                pt_data_to_update.shift_day_adherences(0)
                pt_data_to_update.shift_dichot_day_adherences(0)
                # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
                pt_data_to_update.calc_avg_adherence()
                # Now since adherence for yesterday was 0, we update whether the patient could have been disconnected
                # for multiple (i.e. 2+) days.
                # If patient was also disconnected as evaluated yesterday aka 1 day ago,
                if pt_data_to_update.possibly_disconnected_day1 == True:
                    # Then we shift that indicator back a day and keep day1 disconnect true
                    pt_data_to_update.possibly_disconnected_day2 = True
                    # We update the current variable that yes, today they were possibly_disconnected after 2 days
                    # of 0 adherence / not in Pillsy data
                    pt_data_to_update.possibly_disconnected = True
                    # We increment the number of times this patient was flagged for possibly disconnected
                    pt_data_to_update.num_possibly_disconnected_indicator_true += 1
                    # We add yesterday's date to the possibly disconnected date and list of those dates as well
                    pt_data_to_update.possibly_disconnected_date = yesterday
                    pt_data_to_update.dates_possibly_disconnected.append(yesterday)
                else:
                    # Else if the patient was not disconnected as evaluated yesterday aka 1 day ago,
                    # We can shift the False on day1 to day2 and update day1 (yesterday's disconnection) to day1
                    # But we do not update the disconnected flag and date/date list because it has only been 1 day
                    # of lack of Pillsy data
                    pt_data_to_update.possibly_disconnected_day2 = False
                    pt_data_to_update.possibly_disconnected_day1 = True

            # Now we have updated the patient data to add for the patients without any Pillsy entries from yesterday
            pt_data_to_update.reward_value = 0
            pt_dict_without_reward[pt] = pt_data_to_update

        return pt_dict_with_reward, pt_dict_without_reward


