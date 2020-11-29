from datetime import datetime, date, timedelta
import pandas as pd
import pytz
<<<<<<< HEAD

def import_Pillsy():
    import pandas as pd
    fp = "/Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/Pillsy/2020-11-18_pillsy.csv"
=======
import pickle
from input.data_input_functions import import_Pillsy, import_redcap, load_dict_pickle
from preprocessing.pillsy import get_pillsy_study_ids, find_rewards, update_pt_dict, find_patient_rewards
from ranking.driverRank import run_ranking, write_sms_history
from rewarding.driverReward import send_rewards, get_reward_update
from preprocessing.redcap import update_patient_dict_redcap
from output.data_output_functions import export_pt_dict_pickle, export_post_reward_pickle, write_pt_data_csv
import sys
import time
import dateutil
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankRequest
from msrest.authentication import CognitiveServicesCredentials
import pandas as pd
import numpy as np
import math
import time
from datetime import datetime
from collections import Counter
import string
import pickle
import json
from dateutil import parser
from data_classes.Patient import Patient

def import_Pillsy():
    fp = "/Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/sample_datasets_input/2020-11-17_pillsy.csv"
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
    date_cols = ["eventTime"]
    pillsy = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    pillsy.drop("patientId", axis=1, inplace=True)
    pillsy.drop("lastname", axis=1, inplace=True)
    pillsy.drop("method", axis=1, inplace=True)
    pillsy.drop("platform", axis=1, inplace=True)
    return pillsy



<<<<<<< HEAD

from datetime import datetime, date, timedelta
pillsy = import_Pillsy()
=======
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

def import_Pillsy():
    fp = "/Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/sample_datasets_input/2020-11-17_pillsy.csv"
    try:
        pillsy = pd.read_csv(fp)
    except FileNotFoundError:
        return None
    pillsy["eventTime"] = pd.to_datetime(converter(pillsy["eventTime"]))
    # Note: In this dataset our study_id is actually 'firstname', hence the drop of patientId
    # Note: firstname is currently read in as int64 dtype
    pillsy.drop(["patientId", "lastname", "method", "platform"], axis=1, inplace=True)
    return pillsy


from datetime import datetime, date, timedelta
pilldata = import_Pillsy()
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
yesterday = pytz.UTC.localize(datetime(2020,11,17,10,30))
today = date(2020,11,18)
midnight = pytz.UTC.localize(datetime.combine(today, datetime.min.time()))

<<<<<<< HEAD
pillsy_subset = pillsy[pillsy["firstname"] == 15].copy()
=======
pillsy_subset = pilldata[pilldata["firstname"] == 15].copy()
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
pillsy_yesterday_subset = pillsy_subset[pillsy_subset["eventTime"] < midnight].copy()
pillsy_yesterday_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday].copy()
pillsy_today_subset = pillsy_subset[midnight <= pillsy_subset["eventTime"]].copy()


<<<<<<< HEAD
for index, row in drug_subset.iterrows():
    if row['eventValue'] == "OPEN":
        first_time = row['eventTime'].values[0]
        print(first_time)


def get_drugName_list(patient_entries):
    drugNames_df = patient_entries['drugName']
    unique_drugNames_df = drugNames_df.drop_duplicates()
    unique_drugNames_df_list = unique_drugNames_df.values.tolist()
    return unique_drugNames_df_list


=======

pickle_path = "/Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/sample_datasets_input/2020-11-21_patient_dict.pickle"
with open(pickle_path, 'rb') as pfile:
    pt_dict = pickle.load(pfile)

last_timestamp = "10:30 AM EST " + "2020-11-16"
last_runtime = dateutil.parser.parse(last_timestamp)

for pt in pt_dict:
    patient = pt_dict.get(pt)
    patient.last_run_time = last_runtime


timestamp = "10:30 AM EST " + "2020-11-17"
run_time = dateutil.parser.parse(timestamp)

pt15 = pt_dict.get(15)    

updatedpt15 = find_patient_rewards(pillsy_subset, pt15, run_time)



pillsy_study_ids_list = get_pillsy_study_ids(pilldata)
pt_dict_with_reward, pt_dict_without_reward = find_rewards(pilldata,pillsy_study_ids_list,pt_dict,run_time)


fp = "/Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/sample_datasets_input/2020-11-23_redcap.csv"
date_cols = ["start_date"]
redcap = pd.read_csv(fp, sep=',', parse_dates=date_cols)
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
