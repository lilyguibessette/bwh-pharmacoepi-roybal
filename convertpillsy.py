import pandas as pd
import sys
import os
import re
import gc
import time
import datetime
from datetime import datetime
from collections import Counter
import string
import pickle
import json

#handle case of patient on 2 BID Rxs

class PillsyEntry:
    def __init__(self, firstname, drugName, eventValue, eventTime):
        self.study_id = firstname
        self.drugName = drugName
        self.eventValue = eventValue
        self.eventTime = eventTime


# reward status =
def import_Pillsy(filepath):
    date_cols = ["eventTime"]
    pillsy = pd.read_csv(filepath, sep=',', parse_dates=date_cols)
    print(pillsy['eventTime'].dtypes)
    #pillsy["eventTime"].map(pd.to_datetime())
    pillsy.drop("patientId", axis=1, inplace=True)
    pillsy.drop("lastname",axis=1, inplace=True)
    pillsy.drop("method",axis=1, inplace=True)
    pillsy.drop("platform",axis=1, inplace=True)
    #print("Printing dataframe")
    #print(pillsy)
    #print("Printing dtypes")
    #print(pillsy.dtypes)
    #print("Printing eventTime Column")
    #print(pillsy.eventTime)
    #print("Printing eventTime Column Subtraction")
    #print("Date 1: ", pillsy.eventTime[10])
    #print("Date 2: ", pillsy.eventTime[2])
    #print(pillsy.eventTime[10] - pillsy.eventTime[0])
    return pillsy

def convert_pillsy_to_list(pillsy):
    pillsy_list = list(zip(pillsy.firstname, pillsy.drugName, pillsy.eventValue, pillsy.eventTime))
    print(pillsy_list)
    #print(pillsy_list[0])
    #print(pillsy_list[0][3])
    #print(pillsy_list[10][3] - pillsy_list[0][3])
    return pillsy_list

def get_pillsy_study_ids(pillsy):
    study_ids_df = pillsy['firstname']
    #print(study_ids_df)
    unique_study_ids_df = study_ids_df.drop_duplicates()
    #study_ids_df = study_ids_df.drop_duplicates(['firstname'])
    #print(unique_study_ids_df)
    unique_study_ids_list = unique_study_ids_df.values.tolist()
    #print("printing list\n")
    #print(unique_study_ids_list)
    return unique_study_ids_list

def get_drugName_list(patient_entries):
    drugNames_df = patient_entries['drugName']
    unique_drugNames_df = drugNames_df.drop_duplicates()
    unique_drugNames_df_list = unique_drugNames_df.values.tolist()
    return unique_drugNames_df_list

def identify_drug_freq(drugName):
    if drugName.find('QD') > -1:
        drugFreq = 1
    elif drugName.find('BID') > -1:
        drugFreq = 2
    return drugFreq

def subtract_today(date1, date2):
    return date1 - date2

def find_rewards(pillsy, study_ids_list):
    for study_id in study_ids_list:
        patient_entries = pillsy[pillsy["firstname"] == study_id].copy()
        print(patient_entries)
        patient_drugNames = get_drugName_list(patient_entries)
        print(patient_drugNames)
        for drug in patient_drugNames:
            drug_freq = identify_drug_freq(drug)
            reward_counter = 0
            print(drug_freq)
            patient_by_drug = patient_entries[patient_entries["drugName"] == drug].copy()
            print(patient_by_drug)
            currentday = datetime.now()
            currentday = currentday.replace(tzinfo=None)
            #print("Current Date: " + currentday.__str__())
            #print("DF Date: ")
            #print(patient_by_drug["eventTime"].dtypes)
            new_eventTime = currentday - patient_by_drug.eventTime.astype('datetime64[ns]')
            patient_by_drug['new_eventTime'] = new_eventTime
            print("OLD patient_by_drug")
            print(patient_by_drug["eventTime"])
            print("NEW patient_by_drug")
            print(patient_by_drug["new_eventTime"])
            patient_by_date = patient_by_drug[patient_by_drug.new_eventTime.copy() < pd.Timedelta('1 days')]
            print("subset patient_by_date < 1 day")
            print(patient_by_date)
            patient_by_date = patient_by_date[patient_by_date.new_eventTime.copy() >= pd.Timedelta('0 second')]
            print("subset patient_by_date >= 0 s ")
            print(patient_by_date)
            if not patient_by_date.empty:
                lastOpen= datetime(2000, 1, 1, tzinfo=None)
                lastClose = datetime(2020, 1, 1, tzinfo=None)
                print("preset lastOpen, preset lastClose")
                print(lastOpen, ' --- ', lastClose)

                for index, row in patient_by_date.iterrows():
                    if row['eventValue'] == "OPEN":
                        lastOpen = row['eventTime']
                    elif row['eventValue'] == "CLOSE":
                        lastClose = row['eventTime']
                    diff = lastClose.replace(tzinfo=None) - lastOpen.replace(tzinfo=None)
                    print("lastOpen, lastClose, diff")
                    print(lastOpen, " --- ", lastClose, " --- ", diff)
                #print(lastClose)
                #print(diff)
                    if  pd.Timedelta('0 days 0 hours 0 seconds') <= diff < pd.Timedelta('0 days 3 hours'):
                        reward_counter += 1
                        print("reward_counter:")
                        print(reward_counter)
                        print("close - open:")
                        print(diff)
                        if reward_counter == drug_freq:
                            reward = True
                            print("True")

    return



if __name__ == '__main__':
    pillsy = import_Pillsy("/Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/data/Naming Convention - for Lily.csv")
    # patientId	firstname	lastname	drugName	eventValue	eventTime	method	platform
    pillsy_list = convert_pillsy_to_list(pillsy)
    study_ids_list = get_pillsy_study_ids(pillsy)
    find_rewards(pillsy, study_ids_list)




