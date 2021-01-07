#!/usr/bin/env python
# coding: utf-8

import sys
import time
import dateutil
import dateutil.parser
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankRequest
from msrest.authentication import CognitiveServicesCredentials
import pandas as pd
import numpy as np
import math
import time
from datetime import datetime, timedelta
from collections import Counter
import string
import pickle
import json
import pytz
import os
import re

from patient_data import import_pt_data, new_empty_pt_data
from pillsy_parser import import_Pillsy, find_rewards
from driverReward import get_reward_update,send_rewards
from redcap_parser import import_redcap, update_pt_data_with_redcap
from driverRank import run_ranking, write_sms_history, new_empty_rank_log, write_rank_log
from control_disconnection import check_control_disconnectedness, import_redcap_control, import_pt_data_control
from exe_functions import build_path


## 1. Get date

############# For real deal #############
# run_time = datetime.now()
# run_time = pytz.timezone("America/New_York").localize(run_time)
#########################################

############## For testing ##############
while True:
    try:
        run_time = datetime.strptime(input("Enter YYYY-MM-DD testing date (time will be 9:30 AM): "), "%Y-%m-%d")
        if run_time.year in [2020, 2021]:
            run_time = run_time + timedelta(hours=9, minutes=30)
            break
        else:
            print("testing year must be 2020 or 2021")
    except ValueError as ve:
        print(ve)
# run_time = pytz.timezone("America/New_York").localize(dateutil.parser.parse("10:30 AM 2020-12-15"))
run_time = pytz.timezone("America/New_York").localize(run_time)
print("successful date entered\nrun_time: {}".format(run_time))
#########################################

## 2. Check if program has been run today

fp = build_path("_ProgramLog", str(run_time.date()) + "_RL_Personalizer_log.txt")
if os.path.isfile(fp): 
    input("\nALREADY RAN TODAY: {}.\n".format(run_time.strftime("%B %d, %Y"))
          + "Please contact the other RAs to confirm someone else has already run it today.\n"
          + "Press Enter to exit the program and close this window.")
    sys.exit()

## 3. Ask if first day of trial 

# Embedded this into the import_pt_data, import_pt_data_control, import_Pillsy functions
# while True:
#     first_day = input("\nIs today the trial initiation?\n" 
#                       + "If today is the first day, type 'yes' then hit Enter.\n"
#                       + "Otherwise type 'no' then hit Enter.\n"
#                       + "Answer here: ").lower()
#     if first_day in ["yes", "no"]:
#         first_day = first_day == "yes"
#         break
#     else:
#         print("Input was not 'yes' or 'no'. Please try again.")

## 4. Check for (non)existence of files

pt_data = import_pt_data(run_time)
pt_data_control = import_pt_data_control(run_time)
new_pillsy_data = import_Pillsy(run_time)
redcap_data = import_redcap(run_time)
redcap_control = import_redcap_control(run_time)

## 5. Start log for program

old_stdout = sys.stdout        
log_file = open(fp, "w")
sys.stdout = log_file

## 6. Start main body of program

print("-----------------------------BEGIN PROGRAM----------------------------")
print(run_time)

## Set Up MS Azure Personalizer Client
print("-----------------------------CREATE PERSONALIZER CLIENT----------------------------")
with open(build_path(".keys", "azure-personalizer-key.txt"), 'r') as f:
     personalizer_key = f.read().rstrip()
client = PersonalizerClient(
    "https://bwh-pharmacoepi-roybal-dev-use2-cog.cognitiveservices.azure.com/", 
    CognitiveServicesCredentials(personalizer_key)
)


# ## Reward Step
# 
# If we've already initiated the trial, we will have:
# * Pre-existing patient dataset in need of reward updates
# * Pillsy data from yesterday to determine reward
# If this is study initiation, this step will just load an empty patient dictionary and null pillsy dataset.

# In[5]:



if not pt_data.empty and new_pillsy_data is not None:
    print("----------------------------IMPORT PILLSY AND PT DATA SUCCESS---------------------------")
    print("----------------------------------RUNNING FIND REWARDS----------------------------------")
    # From Pillsy data, computes the Rewards to send to Personalizer for each patient's Rank calls from yesterday's run.
    pt_data = find_rewards(new_pillsy_data, pt_data, run_time)
    print("---------------------------FORMATTING REWARDS FOR PERSONALIZER--------------------------")
    # using updated patient data (new pillsy + patient data), format the rewards to Personalizer into a dataframe
    rewards_to_send = get_reward_update(pt_data, run_time)
    print("-----------------------------SENDING REWARDS TO PERSONALIZER----------------------------")
    # actual call to personalizer
    send_rewards(rewards_to_send, client)


# ## Import/Update Patients

# In[6]:


print("-----------------------------IMPORT REDCAP AND PT DATA----------------------------")
pt_data = update_pt_data_with_redcap(redcap_data, pt_data, run_time)


# ## Rank Step
# Call Personalizer to rank action features to find the correct text message to send today.

# In[7]:


ranked_pt_data = new_empty_pt_data()
ranking_log = new_empty_rank_log(run_time)
print("---------------------------------RANKING PATIENTS---------------------------------")
for index, patient in pt_data.iterrows():
    if patient["censor"] != 1 and patient["censor_date"] > run_time.date():
        patient, pt_rank_log = run_ranking(patient, client, run_time)
        ranked_pt_data = ranked_pt_data.append(patient)
        ranking_log = ranking_log.append(pt_rank_log)

print("---------------------------------EXPORT RANK LOG FILE-----------------------------")
write_rank_log(ranking_log, run_time)
# ## Output SMS and Patient Data

# In[8]:
print("---------------------------------CHECKING CONTROLS---------------------------------")
check_control_disconnectedness(new_pillsy_data,redcap_control,pt_data_control,run_time) # check whether controls have connection problems

print("---------------------------------EXPORT SMS FILE----------------------------------")
write_sms_history(ranked_pt_data, run_time)
ranked_pt_data.to_csv(
    build_path("000_PatientData", str(run_time.date()) + "_pt_data.csv"), 
    index=False
)



print("-----------------------------------------------------------------------------------")
log_file.close()
sys.stdout = old_stdout

print("---------------------------------PROGRAM SUCCESSFULLY RAN--------------------------")
input("SUCCESSFULLY RAN TODAY: {} \n".format(run_time.strftime("%B %d, %Y"))
        + "Now, send messages to patients from /000_SMS_TO_SEND/" + str(run_time.date()) + "_sms_history.csv"
        + "\nPress Enter to exit the program and close this window.")
sys.exit()
