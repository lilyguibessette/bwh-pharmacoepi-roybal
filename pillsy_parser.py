import pandas as pd
import numpy as np
import sys
import os
import re
import gc
import time
from datetime import datetime, date, timedelta
import pytz

from patient_data import get_study_ids, new_empty_pt_data
from exe_functions import build_path


def import_Pillsy(run_time, first_day):
    """Import Pillsy pill taking history as pd.DataFrame from CSV
    """
    
    import_date = (run_time - pd.Timedelta("1 day")).date()
    pillsy_filename = str(import_date) + "_pillsy.csv"
    fp = build_path("Pillsy", pillsy_filename)

    try:
        pillsy = pd.read_csv(fp)
    except FileNotFoundError:
        if not first_day:
            input(str(import_date) + "_pillsy.csv was not found in the Pillsy folder.\n"
                  + "This should be yesterday's date in YYYY-MM-DD format followed by _pillsy.csv\n"
                  + "and this must be placed in the Pillsy folder.\n"
                  + "For example, if today is December 6th, 2020, this should be 2020-12-05_pillsy.csv.\n"
                  + "Please make sure this data has been downloaded and named properly.\n"
                  + "Please run the program again after fixing the file name.\n"
                  + "Press Enter to exit the program and close this window.")
            sys.exit()
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
        return time_string.replace(tz_abbr, tz_ref.get(tz_abbr, "-0500"))

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


def find_taken_events(drug, drug_subset):
    """
    find_taken_events function finds the adherence for a particular drug when run over a particular time period using
    the investigator specified algorithm for evaluating OPEN/CLOSE sequences as taken events
    (Note: 
    Ways to identify Taken Events:
        1. OPEN 
        2. CLOSE CLOSE (within 15 min of each other)
        3. CLOSE OPEN  (within 15 min of each other)
        4. if drug_freq > 1, then for second taken event only need OPEN/CLOSE with wait time of 2 hr 45 min after first
    After identifying first taken event, need to wait 2 hr 45 min to identify second taken event if drug_freq == 2
    :param drug:
    :param drug_subset:
    :return:
    """
#     fifteen_min = pd.Timedelta('15 minutes')
#     two_hr_45_min = pd.Timedelta('2 hours, 45 minutes')
    drug_freq = identify_drug_freq(drug)
    taken = 0
    last_event = None
    waiting_after_close = True
    for index, event in drug_subset.iterrows():
        if last_event is None:
            if event['eventValue'] == "OPEN":
                if drug_freq == 1:
                    return 1.0
                taken += 1
                last_event = event
            else:
                last_event = event
                waiting_after_close = True
        else:
            if waiting_after_close:
                if last_event['eventTime'] + pd.Timedelta('15 minutes') > event['eventTime']:
                    if drug_freq == 1:
                        return 1.0
                    taken += 1
                    last_event = event
                waiting_after_close = False # either way, 15 min passed or taken event occurred
            else:
                if last_event['eventTime'] + pd.Timedelta('2 hours, 45 minutes') < event['eventTime']:
                    return 1.0 # must be second taken event
    return 0.5

def compute_taken_over_expected(patient, timeframe_pillsy_subset, num_pillsy_meds):
    """
    compute_taken_over_expected function runs find_taken_events for each drug to find the adherence of each drug
    over a given time frame and then computes the average adherence for the time period by dividing the sum of
    adherence of all drugs over the number of drugs (i.e. expected maximum sum of adherence) for a patient
    :param patient:
    :param timeframe_pillsy_subset:
    :return:
    """
    timeframe_drugs = get_drugName_list(timeframe_pillsy_subset)
    print("timeframe_drugs:", timeframe_drugs)
    timeframe_adherence_by_drug = [0] * len(timeframe_drugs)
    drug_num = 0
    for drug in timeframe_drugs:
        drug_num += 1
        drug_subset = timeframe_pillsy_subset[timeframe_pillsy_subset['drugName'] == drug]
        this_drug_adherence = find_taken_events(drug, drug_subset)
        timeframe_adherence_by_drug.append(this_drug_adherence)
    taken_over_expected = 0
    if not patient.empty and num_pillsy_meds > 0:
        sum_timeframe_adherence = sum(timeframe_adherence_by_drug)
        taken_over_expected = sum_timeframe_adherence / num_pillsy_meds
        print("timeframe_adherence_by_drug:", timeframe_adherence_by_drug)
        print("sum_timeframe_adherence:", sum_timeframe_adherence)
        print("num_pillsy_meds:", num_pillsy_meds)
        print("taken_over_expected:", taken_over_expected)
    else:
        taken_over_expected = 0
    return taken_over_expected



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
    return patient

    

def find_patient_rewards(pillsy_subset, patient, run_time):
    # From pillsy_subset, get timezone of patient, then use that to calculate the time cut points so that it is relative to the
    # patient's view of time.
    curtime = run_time
    tzinfo_first_row = run_time.tzinfo
    first_row = pillsy_subset.head(1)
    if not first_row.empty:
        #print(first_row['eventTime'].values[0])
        tzinfo_first_row = first_row['eventTime'].values[0].tzinfo
        curtime = curtime.astimezone(tzinfo_first_row)
        
    seven_day_ago = (curtime - timedelta(days=7)).date()
    seven_day_ago_12am = datetime.combine(seven_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)    
    
    six_day_ago = (curtime - timedelta(days=6)).date()
    six_day_ago_12am = datetime.combine(six_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)    
    
    five_day_ago = (curtime - timedelta(days=5)).date()
    five_day_ago_12am = datetime.combine(five_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)
        
    four_day_ago = (curtime - timedelta(days=4)).date()
    four_day_ago_12am = datetime.combine(four_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)
    
    three_day_ago = (curtime - timedelta(days=3)).date()
    three_day_ago_12am = datetime.combine(three_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)
    
    two_day_ago = (curtime - timedelta(days=2)).date()
    two_day_ago_12am = datetime.combine(two_day_ago, datetime.min.time()).astimezone(tzinfo_first_row)
    
    yesterday = (curtime - timedelta(days=1)).date()
    yesterday_12am =datetime.combine(yesterday, datetime.min.time()).astimezone(tzinfo_first_row)
    
    today_current_time = curtime
        # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
    today_12am = datetime.combine(today_current_time, datetime.min.time()).astimezone(tzinfo_first_row)
        
    pillsy_seven_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < six_day_ago_12am]
    pillsy_seven_day_ago_subset = pillsy_seven_day_ago_subset[pillsy_seven_day_ago_subset["eventTime"] >= seven_day_ago_12am]

    pillsy_six_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < five_day_ago_12am]
    pillsy_six_day_ago_subset = pillsy_six_day_ago_subset[pillsy_six_day_ago_subset["eventTime"] >= six_day_ago_12am]

    pillsy_five_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < four_day_ago_12am]
    pillsy_five_day_ago_subset = pillsy_five_day_ago_subset[pillsy_five_day_ago_subset["eventTime"] >= five_day_ago_12am]

    pillsy_four_day_ago_subset = pillsy_subset[pillsy_subset["eventTime"] < three_day_ago_12am]
    pillsy_four_day_ago_subset = pillsy_four_day_ago_subset[pillsy_four_day_ago_subset["eventTime"] >= four_day_ago_12am]

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
    
    print("-----------------------------BEGIN CHECKING REWARDS FOR PT ", patient["record_id"], "----------------------------")
    print("record_id:", patient["record_id"])
    
    print("Computing... reward_value_t0 in pillsy_yesterday_subset with # med:", patient["num_pillsy_meds_t0"])
    reward_value_t0 = compute_taken_over_expected(patient, pillsy_yesterday_subset, patient["num_pillsy_meds_t0"])
    print("reward_value_t0:", reward_value_t0)
    print("Computing... reward_value_t1 in pillsy_two_day_ago_subset with # med:", patient["num_pillsy_meds_t1"])
    reward_value_t1 = compute_taken_over_expected(patient, pillsy_two_day_ago_subset, patient["num_pillsy_meds_t1"])
    print("reward_value_t1:", reward_value_t1)

    adherence_day3 = compute_taken_over_expected(patient, pillsy_three_day_ago_subset, patient["num_pillsy_meds_t2"])
    adherence_day4 = compute_taken_over_expected(patient, pillsy_three_day_ago_subset, patient["num_pillsy_meds_t3"])
    adherence_day5 = compute_taken_over_expected(patient, pillsy_three_day_ago_subset, patient["num_pillsy_meds_t4"])
    adherence_day6 = compute_taken_over_expected(patient, pillsy_three_day_ago_subset, patient["num_pillsy_meds_t5"])
    adherence_day7 = compute_taken_over_expected(patient, pillsy_three_day_ago_subset, patient["num_pillsy_meds_t6"])
   
    
    print("Computing... early_rx_use in pillsy_early_today_subset with # med:", patient["num_pillsy_meds_t0"])
    early_rx_use = compute_taken_over_expected(patient, pillsy_early_today_subset, patient["num_pillsy_meds_t0"])
    print("early_rx_use:", early_rx_use)
    
    print("Computing... yesterday_disconnectedness in pillsy_yesterday_disconnectedness_subset with # med:", patient["num_pillsy_meds_t0"])
    observed_num_drugs = get_drugName_list(pillsy_yesterday_disconnectedness_subset)
    print("expected # rx:",  patient["num_pillsy_meds_t0"],"// observed # rx:", len(observed_num_drugs), "\n observed rx names:",observed_num_drugs)
    
    # if we didn't send reward for 2 days ago yesterday, we send it today
    if patient["flag_send_reward_value_t1"] == False:
        patient["flag_send_reward_value_t1"] = True   
    
    # now we check to see if we should send yesterday's reward today 
    if len(observed_num_drugs) == patient["num_pillsy_meds_t0"]:
        yesterday_disconnectedness = 1
        # patient is connected so we can send the reward for yesterday
        patient["flag_send_reward_value_t0"] = True
    else:
        # patient is disconnected so we will give it some time to back fill and send tomorrow
        yesterday_disconnectedness = -1
        patient["num_dates_disconnectedness"] += 1
        patient["flag_send_reward_value_t0"] = False   
    print("disconnectedness:", yesterday_disconnectedness)

    # Update data frame with new values for reward and
    patient["reward_value_t0"] = reward_value_t0
    patient["reward_value_t1"] = reward_value_t1
    patient["early_rx_use"] = early_rx_use
    
    if early_rx_use > 0:
        patient["num_dates_early_rx_use"] += 1

    patient["adherence_day7"] = adherence_day7
    patient["adherence_day6"] = adherence_day6
    patient["adherence_day5"] = adherence_day5
    patient["adherence_day4"] = adherence_day4
    patient["adherence_day3"] = adherence_day3
    patient["adherence_day2"] = reward_value_t1
    patient["adherence_day1"] = reward_value_t0
    
    patient["dichot_adherence_day7"] = (adherence_day7 > 0)*1
    patient["dichot_adherence_day6"] = (adherence_day6 > 0)*1
    patient["dichot_adherence_day5"] = (adherence_day5 > 0)*1
    patient["dichot_adherence_day4"] = (adherence_day4 > 0)*1
    patient["dichot_adherence_day3"] = (adherence_day3 > 0)*1
    patient["dichot_adherence_day2"] = (reward_value_t1 > 0)*1
    patient["dichot_adherence_day1"] = (reward_value_t0 > 0)*1
   
    # We update the avg adherences at days 1,3,7 with updated shifted daily adherence values:
    patient = calc_avg_adherence(patient)

    return patient 

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
    rewarded_pt_data = new_empty_pt_data()
    study_ids_list = get_study_ids(pt_data)
    for study_id in study_ids_list:
        # Filter by firstname = study_id to get data for just this one patient
        patient_pillsy_subset = pillsy[pillsy["firstname"] == study_id]
        patient_row = pt_data[pt_data["record_id"] == study_id].iloc[0]
        # This function will update the patient attributes with the updated adherence data that we will find from pillsy
        patient_row = find_patient_rewards(patient_pillsy_subset, patient_row, run_time)
        rewarded_pt_data = rewarded_pt_data.append(patient_row)
    return rewarded_pt_data


