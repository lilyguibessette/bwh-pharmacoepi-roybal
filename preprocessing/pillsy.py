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

def get_drugName_list(patient_entries):
    drugNames_df = patient_entries['drugName']
    unique_drugNames_df = drugNames_df.drop_duplicates()
    unique_drugNames_df_list = unique_drugNames_df.values.tolist()
    return unique_drugNames_df_list

def get_pillsy_study_ids(pillsy):
    # Subsets the firstname column to find the unique study_id's available in the Pillsy data to update adherence
    study_ids_df = pillsy['firstname']
    unique_study_ids_df = study_ids_df.drop_duplicates()
    unique_study_ids_list = unique_study_ids_df.values.tolist()
    return unique_study_ids_list

def identify_drug_freq(drugName):
    # drugName is a String
    # .find returns -1 if it doesn't find the String QD or BID in the drugName String
    # If the drugName does contain QD or BID, then .find() will return an int > -1 (0 or more)
    # at the index of the first occurence of the BID or QD string
    if drugName.find('QD') > -1:
        drugFreq = 1
    elif drugName.find('BID') > -1:
        drugFreq = 2
    # Returns the number of doses that the given Medication is
    return drugFreq

def update_pt_dict(pt_dict_with_reward, pt_dict_without_reward):
    updated_pt_dict = {**pt_dict_with_reward, **pt_dict_without_reward}
    return updated_pt_dict

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

    sum_yesterday_adherence = sum(yesterday_adherence_by_drug)
    taken_over_expected = sum_yesterday_adherence / patient.num_pillsy_meds
    return taken_over_expected


def find_patient_rewards(pillsy_subset, patient):
    yesterday = patient.last_run_time
    yesterday_12am = pytz.UTC.localize(datetime.combine(yesterday, datetime.min.time()))
    today = date.today()
    # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
    today_12am = pytz.UTC.localize(datetime.combine(today, datetime.min.time()))

    #TODO
    # Quadruple check with Julie that this time frame makes sense...
    pillsy_yesterday_subset = pillsy_subset[pillsy_subset["eventTime"] < today_12am].copy()
    pillsy_yesterday_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday].copy()

    pillsy_calendar_day_subset = pillsy_subset[pillsy_subset["eventTime"] >= yesterday_12am].copy()
    pillsy_calendar_day_subset = pillsy_calendar_day_subset[pillsy_calendar_day_subset["eventTime"] < today_12am].copy()

    pillsy_today_subset = pillsy_subset[pillsy_subset["eventTime"] >= today_12am].copy()

    yesterday_taken_over_expected = compute_taken_over_expected(patient, pillsy_yesterday_subset)

    # Use last call to today 12am time frame for reward
    patient.reward_value = yesterday_taken_over_expected

    # Use calendar day of yesterday to compute adherence
    todays_avg_adherence = compute_taken_over_expected(patient, pillsy_calendar_day_subset)

    # Shifts the adherence for each day backwards by 1 day to make day1 = newest found avg_adherence
    # and day2 = old day, day3 = old day 2... etc day7 = old day 6
    patient.shift_day_adherences(todays_avg_adherence)
    patient.shift_dichot_day_adherences(todays_avg_adherence)
    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
    patient.calc_avg_adherence()
    # Add this updated patient with new data to the patient to the pt_dict_with_reward that will be used
    # to updated Personalizer of rewards
    #TODO figure out if this is true or not
    # patient.reward_value = todays_avg_adherence

    early_use_proportion = compute_taken_over_expected(patient, pillsy_today_subset)
    if early_use_proportion == 1:
        patient.early_rx_use_before_sms = 1

    return patient

def find_rewards(pillsy, pillsy_study_ids_list, pt_dict):
        pt_dict_with_reward = {}
        for study_id in pillsy_study_ids_list:
            # Filter by firstname = study_id to get data for just this one patient
            pillsy_subset = pillsy[pillsy["firstname"] == study_id].copy()
            # Now we will send our current patient object to the find_patient_rewards function with their study_id & pillsy subset
            patient = pt_dict.get(study_id) # Gets current patient from study_id
            # This function with update the patient attributes with the updated adherence data that we will find from pillsy
            updated_patient = find_patient_rewards(pillsy_subset, patient)
            # The function returns an updated patient
            # We add this patient to our originally empty pt_dict_with_reward dictionary with their study_id as a key
            pt_dict_with_reward[study_id] = updated_patient

        # Now that we've iterated through all patients in the Pillsy data, we identify the patients not found at all
        # Therefore these patients do not have any rewards to send to Personalizer, but we still need to update them and
        # shift their adherence and also add indicators that they may be disconnected.
        pt_dict_without_reward = {}

        # Store Yesterday's date if needed
        yesterday = date.today() - timedelta(days=1)
        for pt, pt_data_to_update in pt_dict.items():
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
                    # But w  e do not update the disconnected flag and date/date list because it has only been 1 day
                    # of lack of Pillsy data
                    pt_data_to_update.possibly_disconnected_day2 = False
                    pt_data_to_update.possibly_disconnected_day1 = True

            # Now we have updated the patient data to add for the patients without any Pillsy entries from yesterday
            pt_data_to_update.reward_value = 0
            pt_dict_without_reward[pt] = pt_data_to_update

        return pt_dict_with_reward, pt_dict_without_reward

