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
    importPillsy()




## Steps - Import baseline demographics to start
## ask julie if all patients will start on same day