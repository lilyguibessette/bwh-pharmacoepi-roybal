import pandas as pd
import sys
import os
import re
import gc
import time
import datetime
from collections import Counter
import string
import pickle
import json


def importPillsy(filepath):
    date_cols = ["eventTime"]
    pillsy = pd.read_csv(filepath, sep=',', parse_dates=date_cols)
    print("Printing dataframe")
    print(pillsy)
    print("Printing dtypes")
    print(pillsy.dtypes)
    print("Printing eventTime Column")
    print(pillsy.eventTime)
    print("Printing eventTime Column Subtraction")
    print("Date 1: ", pillsy.eventTime[10])
    print("Date 2: ", pillsy.eventTime[0])
    print(pillsy.eventTime[10] - pillsy.eventTime[0])
    pillsy_list = list(zip(pillsy.patientId, pillsy.drugName, pillsy.eventValue, pillsy.eventTime))
    print(pillsy_list)
    print(pillsy_list[0])
    print(pillsy_list[0][3])
    print(pillsy_list[10][3] - pillsy_list[0][3])


def import_demographics(filepath):
    date_cols = ["eventTime"]
    demographics = pd.read_csv(filepath, sep=',', parse_dates=date_cols)


if __name__ == '__main__':
    lastOpen = datetime(2000, 1, 1, tzinfo=None)
    lastClose = datetime(2040, 1, 1, tzinfo=None)
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
        # print(lastClose)
        # print(diff)
        if pd.Timedelta('0 days 0 hours 0 seconds') <= diff < pd.Timedelta('0 days 3 hours'):


## Steps - Import baseline demographics to start
## ask julie if all patients will start on same day