#!/usr/bin/env python
# coding: utf-8

# ## Reinforcement Learning for SMS Messaging to Improve Medication Adherence - Roybal

# In[17]:


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
from datetime import datetime
from collections import Counter
import string
import pickle
import json
import pytz
import os
import re


# In[18]:


from patient_data import import_pt_data,export_pt_data, new_empty_pt_data
from pillsy_parser import import_Pillsy, find_rewards
from driverReward import get_reward_update,send_rewards
from redcap_parser import import_redcap, update_pt_data_with_redcap
from driverRank import run_ranking, write_sms_history
from control_disconnection import check_control_disconnectedness


# ### Start Program Timer

# In[19]:


# run_time = datetime.now()
# testing_flag = input("Testing with another date? y/n: ")
# if testing_flag.lower() == "y":
#     print("Set testing run time: ")
#     run_time_yyyy_mm_dd_input = input("Enter the testing date: YYYY-MM-DD ")
#     timestamp = "10:30 AM " + run_time_yyyy_mm_dd_input
#     run_time = dateutil.parser.parse(timestamp)
# run_time = pytz.timezone("America/New_York").localize(run_time)
# run_time

run_time = pytz.timezone("America/New_York").localize(dateutil.parser.parse("10:30 AM 2020-12-06"))
run_time 

old_stdout = sys.stdout
name = str(run_time.date()) + "_RL_Personalizer_log.txt"
fp = os.path.join("..", "ProgramLog", name)
log_file = open(fp, "w")
sys.stdout = log_file
start_time = time.time()
print("-----------------------------BEGIN PROGRAM----------------------------")
print(start_time)
print(run_time)


# ### Set Up MS Azure Personalizer Client
# 
# Defining and Instantiating a Personalizer Client:
# 
# Personalizer Keys:
# * In the Microsoft Azure Dashboard, navigate to our bwh-pharmacoepi-roybal-dev-use2-cog Cognitive Services page.
# * Within the Keys and Endpoint section, copy either Key 1 or Key 2 to enter as the Personalizer Key.
# 
# Personalizer Endpoint:
# * https://bwh-pharmacoepi-roybal-dev-use2-cog.cognitiveservices.azure.com/

# In[20]:


print("-----------------------------CREATE PERSONALIZER CLIENT----------------------------")
with open(os.path.join("..", ".keys", "azure-personalizer-key.txt"), 'r') as f:
     personalizer_key = f.read().rstrip()
personalizer_endpoint = "https://bwh-pharmacoepi-roybal-dev-use2-cog.cognitiveservices.azure.com/"
client = PersonalizerClient(personalizer_endpoint, CognitiveServicesCredentials(personalizer_key))


# ## Reward Step
# 
# If we've already initiated the trial, we will have:
# * Pre-existing patient dataset in need of reward updates
# * Pillsy data from yesterday to determine reward
# If this is study initiation, this step will just load an empty patient dictionary and null pillsy dataset.

# In[21]:


print("-----------------------------IMPORT PILLSY AND PT DATA----------------------------")
pt_data = import_pt_data(run_time)
new_pillsy_data = import_Pillsy(run_time)

if not pt_data.empty and new_pillsy_data is not None:
    print("----------------------------------RUNNING FIND REWARDS----------------------------------")
    # From Pillsy data, computes the Rewards to send to Personalizer for each patient's Rank calls from yesterday's run.
    pt_data = find_rewards(new_pillsy_data, pt_data, run_time)
    print("---------------------------FORMATTING REWARDS FOR PERSONALIZER--------------------------")
    # using updated patient data (new pillsy + patient data), format the rewards to Personalizer into a dataframe
    rewards_to_send = get_reward_update(pt_data, run_time)
    print("-----------------------------SENDING REWARDS TO PERSONALIZER----------------------------")
    # actual call to personalizer
    send_rewards(rewards_to_send, client)
    export_pt_data(pt_data, run_time, "reward")


# ## Import/Update Patients

# In[22]:


print("-----------------------------IMPORT REDCAP AND PT DATA----------------------------")
redcap_data = import_redcap(run_time)
pt_data = update_pt_data_with_redcap(redcap_data, pt_data, run_time)


# ## Rank Step
# Call Personalizer to rank action features to find the correct text message to send today.

# In[23]:


ranked_pt_data = new_empty_pt_data()
print("---------------------------------RANKING PATIENTS---------------------------------")
for index, patient in pt_data.iterrows():
    if patient["censor"] != 1 and patient["censor_date"] > run_time.date():
        patient = run_ranking(patient, client, run_time)
        ranked_pt_data = ranked_pt_data.append(patient)
export_pt_data(ranked_pt_data, run_time, "rank") # log


# ## Output SMS and Patient Data

# In[24]:


print("---------------------------------EXPORT SMS FILE---------------------------------")
write_sms_history(ranked_pt_data, run_time)
export_pt_data(ranked_pt_data, run_time, "final") # input for tomorrow
print("---------------------------------CHECKING CONTROLS---------------------------------")
check_control_disconnectedness(run_time) # check whether controls have connection problems
print("-----------------------------------------------------------------------------------")
log_file.close()
sys.stdout = old_stdout


# To Do List:
#   *  Make a log file that will report high level information from running this like a run summary
#         * elements to include:
#             * start and end time of the run
#             * how many patients were read in from each import statement
#             * how many reward calls were successfull made
#             * how many rank calls were successfull made
#             * any other meta data that will help us debug and ensure this is all working as planned
# 
# 
# 
