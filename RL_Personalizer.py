#!/usr/bin/env python
# coding: utf-8

# ## Reinforcement Learning for SMS Messaging to Improve Medication Adherence - Roybal

# In[1]:


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


# In[2]:


from patient_data import import_pt_data, new_empty_pt_data
from pillsy_parser import import_Pillsy, find_rewards
from driverReward import get_reward_update,send_rewards
from redcap_parser import import_redcap, update_pt_data_with_redcap
from driverRank import run_ranking, write_sms_history
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

## 2. Ask if first day of trial

while True:
    first_day = input("Is today the trial initiation?\n" 
                      + "If today is the first day, type 'yes' then hit Enter.\n"
                      + "Otherwise type 'no' then hit Enter.\n"
                      + "Answer here: ").lower()
    if first_day in ["yes", "no"]:
        first_day = first_day == "yes"
        break
    else:
        print("Input was not 'yes' or 'no'. Please try again.")

## 3. Check for (non)existence of files

pt_data = import_pt_data(run_time, first_day)
pt_data_control = import_pt_data_control(run_time, first_day)
new_pillsy_data = import_Pillsy(run_time, first_day)
redcap_data = import_redcap(run_time)
redcap_control = import_redcap_control(run_time)
# if first_day:
#     yesterday = (run_time - pd.Timedelta("1 day")).date()
#     if not pt_data.empty:
#         input("There should not be a file named {}_pt_data.csv in the PatientData folder.\n".format(yesterday)
#               + "Yesterday's patient data should not exist yet on the first day.\n"
#               + "If saying that today is the trial initiation was incorrect, just run the program again.\n"
#               + "Otherwise please contact Lily!\n"
#               + "Either way, press Enter to exit the program and close this window.")
#     elif not pt_data_control.empty:
#         input("There should not be a file named {}_pt_data_control.csv in the PatientDataControl folder.\n".format(yesterday)
#               + "Yesterday's patient data should not exist yet on the first day.\n"
#               + "If saying that today is the trial initiation was incorrect, just run the program again.\n"
#               + "Otherwise please contact Lily!\n"
#               + "Either way, press Enter to exit the program and close this window.")
#     sys.exit()

# file_not_found = False
# if pt_data.empty:
#     print("pt_data.empty")
#     file_not_found = True
# if new_pillsy_data is None:
#     print("new_pillsy_data = None")
#     file_not_found = True
# if redcap_data.empty:
#     print("redcap_data.empty")
#     file_not_found = True
# if pt_data_control.empty:
#     print("pt_data_control.empty")
#     file_not_found = True    
# if redcap_control.empty:
#     print("redcap_control.empty")
#     file_not_found = True    
# if file_not_found == True:    
#     print("ERROR - FILE NOT FOUND")
#     start = input("\nIs today the trial initiation? Y/N: ")
#     if start.lower().startswith("n"):
#         print("ERROR - FILE NOT FOUND NOT ANTICIPATED")
#         time.sleep(15)
#         sys.exit()

## 4. Start log for program

fp = build_path("ProgramLog", str(run_time.date()) + "_RL_Personalizer_log.txt")
if os.path.isfile(fp): 
    input("ALREADY RAN TODAY, {}.".format(run_time.strftime("%d %B, %Y"))
          + "Contact the other program runners to confirm someone else has already run it today."
          + "Press Enter to exit the program and close this window.")
    sys.exit()
old_stdout = sys.stdout        
log_file = open(fp, "w")
sys.stdout = log_file

## 5. Start main body of program

start_time = time.time()
print("-----------------------------BEGIN PROGRAM----------------------------")
print(start_time)
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
print("---------------------------------RANKING PATIENTS---------------------------------")
for index, patient in pt_data.iterrows():
    if patient["censor"] != 1 and patient["censor_date"] > run_time.date():
        patient = run_ranking(patient, client, run_time)
        ranked_pt_data = ranked_pt_data.append(patient)


# ## Output SMS and Patient Data

# In[8]:


print("---------------------------------EXPORT SMS FILE---------------------------------")
write_sms_history(ranked_pt_data, run_time)
ranked_pt_data.to_csv(
    build_path("PatientData", str(run_time.date()) + "_pt_data.csv"), 
    index=False
)
# one liner right here^ to replace export_pt_data below
# export_pt_data(ranked_pt_data, run_time, "final") # input for tomorrow
print("---------------------------------CHECKING CONTROLS---------------------------------")
check_control_disconnectedness(new_pillsy_data,redcap_control,pt_data_control,run_time) # check whether controls have connection problems
print("-----------------------------------------------------------------------------------")
log_file.close()
sys.stdout = old_stdout


# To Do List:
#   *  Reward Received check? - Could do through platform
#   *  International Time Zones
#   *  More testing
# 
