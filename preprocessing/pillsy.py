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

from collections import Counter
import string
import pickle
import json
from input.data_input_functions import import_Pillsy

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


def find_patient_rewards(pillsy_subset, patient):
    yesterday = patient.last_run_time
    today = date.today()
    # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
    midnight = pytz.UTC.localize(datetime.combine(today, datetime.min.time()))
    pillsy_yesterday_subset = pillsy_subset[pillsy_subset["eventTime"] < midnight].copy()
    pillsy_yesterday_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday].copy()
    pillsy_today_subset = pillsy_subset[pillsy_subset["eventTime"] >= midnight].copy()


    min_time_between = pd.Timedelta('15 minutes')
    yesterday_drugs = get_drugName_list(pillsy_yesterday_subset)
    yesterday_adherence_by_drug = [0] * len(yesterday_drugs)
    drug_num = 0
    for drug in yesterday_drugs:
        drug_num += 1
        drug_freq = identify_drug_freq(drug)
        taken = 0
        taken_events = []
        maybe_taken_event = None
        drug_subset = pillsy_yesterday_subset[pillsy_yesterday_subset['drugName'] == drug].copy()
        for index, row in drug_subset.iterrows():
            if drug_freq == taken:
                break
            if row['eventValue'] == "OPEN" and not taken_events:
                first_taken = row['eventTime']
                taken_events.append(first_taken)
            elif row['eventValue'] == "CLOSE" and not taken_events:
                maybe_taken_event = row['eventTime']
            elif row['eventValue'] == "OPEN" and taken_events:
                if row['eventTime'] 


            if len(taken_events) != 0:








    # subset into yesterday and today
    # for yesterday
        # get unique medication names as list from the drugName column
        # store this as a
        # for each medication in this list
            # check if BID or QD
            # If QD => simply check if




    todays_avg_adherence = 0
    # ************ TO DO ******************
    # Account for the early_rx_use_before_sms for patients taking medication early before text
    # Subset Pillsy data to the morning of this algorithm being run to find patients that took med early
    # repeat above algorithm


    # Shifts the adherence for each day backwards by 1 day to make day1 = newest found avg_adherence
    # and day2 = old day, day3 = old day 2... etc day7 = old day 6
    patient.shift_day_adherences(todays_avg_adherence)
    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
    patient.calc_avg_adherence()
    # Add this updated patient with new data to the patient to the pt_dict_with_reward that will be used
    # to updated Personalizer of rewards
    patient.reward_value = todays_avg_adherence

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
            # *********** TO DO ******************
            # NEED TO EDIT SINCE I CHANGED THE DATA TYPE AT SOME POINT OF PILLSY AND NEED TO FIX ALL THE SUBSET METHODS
            # *********** TO DO ******************
            #
            # # subset for early today and yesterday
            # patient_drugNames = get_drugName_list(patient_entries)
            # todays_adherence_by_drug = [0] * len(patient_drugNames)
            # drug_num = 0
            # for drug in patient_drugNames:
            #     drug_num += 1
            #     drug_freq = identify_drug_freq(drug)
            #     reward_counter = 0
            #
            #     patient_by_drug = patient_entries[patient_entries["drugName"] == drug].copy()
            #     print(patient_by_drug)
            #     currentday = datetime.now()
            #     currentday = currentday.replace(tzinfo=None)
            #     # print("Current Date: " + currentday.__str__())
            #     # print("DF Date: ")
            #     # print(patient_by_drug["eventTime"].dtypes)
            #     new_eventTime = currentday - patient_by_drug.eventTime.astype('datetime64[ns]')
            #     patient_by_drug['new_eventTime'] = new_eventTime
            #     print("OLD patient_by_drug")
            #     print(patient_by_drug["eventTime"])
            #     print("NEW patient_by_drug")
            #     print(patient_by_drug["new_eventTime"])
            #     ## change to last time called instead of 24 hours
            #     patient_by_date = patient_by_drug[patient_by_drug.new_eventTime.copy() < pd.Timedelta('1 days')]
            #     print("subset patient_by_date < 1 day")
            #     print(patient_by_date)
            #     patient_by_date = patient_by_date[patient_by_date.new_eventTime.copy() >= pd.Timedelta('0 second')]
            #     print("subset patient_by_date >= 0 s ")
            #     print(patient_by_date)

            #     if not patient_by_date.empty:
            #         lastOpen = datetime(2000, 1, 1, tzinfo=None)
            #         lastClose = datetime(2040, 1, 1, tzinfo=None)
            #         print("preset lastOpen, preset lastClose")
            #         print(lastOpen, ' --- ', lastClose)
            #
            #         for index, row in patient_by_date.iterrows():
            #             # *********** TO DO ******************
            #             # NEED TO EDIT TO THE NEW ALGORITHM WITH THE CASES OF 3 MEDICATIONS AND BID VS QD
            #             # *********** TO DO ******************
            #             if row['eventValue'] == "OPEN":
            #                 lastOpen = row['eventTime']
            #             elif row['eventValue'] == "CLOSE":
            #                 lastClose = row['eventTime']
            #             diff = lastClose.replace(tzinfo=None) - lastOpen.replace(tzinfo=None)
            #             print("lastOpen, lastClose, diff")
            #             print(lastOpen, " --- ", lastClose, " --- ", diff)
            #             # print(lastClose)
            #             # print(diff)
            #             if pd.Timedelta('0 days 0 hours 0 seconds') <= diff < pd.Timedelta('0 days 3 hours'):
            #                 reward_counter += 1
            #                 print("reward_counter:")
            #                 print(reward_counter)
            #                 print("close - open:")
            #                 print(diff)
            #                 lastOpen = datetime(2000, 1, 1, tzinfo=None)
            #                 lastClose = datetime(2040, 1, 1, tzinfo=None)
            #     this_adherence = reward_counter / drug_freq
            #     todays_adherence_by_drug.append(this_adherence)
            #     ## handle case if they only took a BID med 1x
            #     ## for BID meds should the patient
            #



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

def get_reward_update(pt_dict_with_reward):
    # Subset updated_pt_dict to what we need for rank calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['reward', 'frame_id', 'history_id', 'social_id', 'content_id', 'reflective_id', 'study_id', 'trial_day_counter']
    reward_updates = pd.DataFrame(columns=column_values)

    for pt, data in pt_dict_with_reward:
        # Reward value, Rank_Id's
        new_row = [data.adherence_day1, data.rank_id_framing, data.rank_id_history,
                   data.rank_id_social, data.rank_id_content, data.rank_id_reflective,
                   data.study_id, data.trial_day_counter]
        reward_updates.loc[len(reward_updates)] = new_row

    reward_updates = reward_updates.to_numpy()
    return reward_updates