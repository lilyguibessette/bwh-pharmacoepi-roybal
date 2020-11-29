#!/usr/bin/env python
# coding: utf-8

# Reinforcement Learning for SMS Messaging to Improve Medication Adherence - Roybal

# Import necessary packages

# In[1]:


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


# Imports from Local Python Code Files

# In[2]:


from input.data_input_functions import import_Pillsy, import_redcap, load_dict_pickle
from preprocessing.pillsy import get_pillsy_study_ids, find_rewards, update_pt_dict
from ranking.driverRank import run_ranking, write_sms_history
from rewarding.driverReward import send_rewards, get_reward_update
from preprocessing.redcap import update_patient_dict_redcap
from output.data_output_functions import export_pt_dict_pickle, export_post_reward_pickle, write_pt_data_csv


# Start Program Timer & Set Up MS Azure Personalizer Client

# In[3]:


start_time = time.time()
run_time = datetime.now()
testing_flag = input("Testing with another date? y/n: ")
if testing_flag.lower() == "y":
    print("Set testing run time: ")
    run_time_yyyy_mm_dd_input = input("Enter the testing date: YYYY-MM-DD ")
    timestamp = "10:30 AM EST " + run_time_yyyy_mm_dd_input
    run_time = dateutil.parser.parse(timestamp)


personalizer_key = input("ENTER PERSONALIZER KEY: \n")

personalizer_endpoint = input("ENTER PERSONALIZER ENDPOINT: \n")


# Defining and Instantiating a Personalizer Client:
# 
# Personalizer Keys:
# * In the Microsoft Azure Dashboard, navigate to our bwh-pharmacoepi-roybal-dev-use2-cog Cognitive Services page.
# * Within the Keys and Endpoint section, copy either Key 1 or Key 2 to enter as the Personalizer Key.
# 
# Personalizer Endpoint:
# * https://bwh-pharmacoepi-roybal-dev-use2-cog.cognitiveservices.azure.com/

# In[4]:


client = PersonalizerClient(personalizer_endpoint, CognitiveServicesCredentials(personalizer_key))


# If we've already initiated the trial, we will have:
# * Pre-existing patient dataset in need of reward updates
# * Pillsy data from yesterday to determine reward
# If this is study initiation, this step will just load an empty patient dictionary and null pillsy dataset.

# In[ ]:


pt_dict = load_dict_pickle(run_time)
new_pillsy_data = import_Pillsy(run_time)
pillsy_updated_pt_dict = {}

# Make sure pt_dict and new_pillsy_data aren't empty or null (i.e. for study initiation).
if not pt_dict and not new_pillsy_data:
# Extract list of study_id's in the Pillsy Data.
    pillsy_study_ids_list = get_pillsy_study_ids(new_pillsy_data)
# From Pillsy data, computes the Rewards to send to Personalizer for each patient's Rank calls from yesterday's run.
    pt_dict_with_reward, pt_dict_without_reward = find_rewards(new_pillsy_data,pillsy_study_ids_list,pt_dict,run_time)
# Using this updated Pillsy joined Patient data, we format the rewards to Personalizer into a dataframe
    rewards_to_send = get_reward_update(pt_dict_with_reward, run_time)
    send_rewards(rewards_to_send, client, run_time)

# Combines the patients with and without rewards to update the patient dataset for the next step of ranking for today's SMS message.
    pillsy_updated_pt_dict = update_pt_dict(pt_dict_with_reward, pt_dict_without_reward)
    export_post_reward_pickle(pillsy_updated_pt_dict, run_time)


# Call Personalizer to rank action features to find the correct text message to send today.

# In[ ]:


redcap_data = import_redcap(run_time)
redcap_updated_pt_dict = update_patient_dict_redcap(redcap_data, pillsy_updated_pt_dict, run_time)
final_pt_dict = {}

for study_id, patient in final_pt_dict.items():
    ranked_patient = run_ranking(patient, client, run_time)
    final_pt_dict[study_id] = patient

write_sms_history(final_pt_dict, run_time)
export_pt_dict_pickle(final_pt_dict, run_time)
write_pt_data_csv(final_pt_dict, run_time)


# To Do List:
# * General -
#     * [x] Lily-DONE - Remove the weird option for if this is start or not, perhaps figure out a way to reduce human choice here
#     * [ ] Lily-STARTED - JOE TODO - Export of log files for rank & reward as pickles - do we want these as CSVs? = JULIE ANSWER - Yes we do
#     * [ ] Lily-pickle,done, need converter like in write_sms_history or get_reward_update- JOE TODO - Export of patient_dict as CSV as well as pickle
#     * Data processing - timezone timestamp issue for datetime data from Pillsy
#     * Automate file import methods based on naming convention of:
#         * [x] Lily-DONE (from Joe's research) YAY- YYYY-MM-DD_recap.csv
#         * [x] Lily-DONE (from Joe's research) YAY- YYYY-MM-DD_pillsy.csv
#         * [x] Lily-DONE (from Joe's research) YAY- YYYY-MM-DD_patient_dict.pickle
# * Pillsy -
#      * [ ] JOE TODO - figure out the tzinfo warning for CDT timezones - need to fix in the import more documentation there for whats going wrong
#     * [x] Lily-DONE YAY- Pseudo code taken event decisions for Joe to code up (did it before, but we made some changes to algorithm)
#     * [x] Lily-DONE YAY - Redo processing algorithm for taken events pseudo code handwritten in notes
#     * [x] Lily-DONE YAY - Fix timing of when this is run - i.e. subset to time frame
#     * [x] Lily-DONE YAY Need variable to store the last time this was run - i.e. should this be user entered or stored?
#     * [x] Lily-DONE YAY  i.e. not from time of last run to current time; will be from last run to defined time of 'early today'
#     * [ ] Another question sent to Elad/Marco/Julie again; JULIE ANSWER algorithm runs from last run to 12am anytime 12am to current time = early use - Need to define what early today is i.e. 2am onwards? - I don't think we defined this yet actually
#     * [x] Lily-DONE-YAY- Account for if patient already took med that day
#         * AKA run above algorithm on data occurring morning of for early_rx_use_before_sms to be true if adherence = 1 already
# * RedCap -
#     * [x] Lily-DONE YAY- Need to work on import method
#     * [ ] Lily-Started- Need to properly encode categorical variables as strings rather than numeric - waiting for confirmation that it is finalized on Julie/constance/ellen side
#     * [ ] Lily-SetUp Complete under this assumption- Need to make sure they can give me a censoring variable from redcap
#     * [x] Lily-DONE YAY- JULIE ANSWER YES (only update for Pillsy Rx and Num 2x meds) - Do we need to account for the RedCap data changing for a patient that is already receiving text messages? i.e. updates to baseline variables coming from red_cap?
# * SMS -
#     * For each patient:
#         * [x] Joe-DONE YAY-Use 1,0's from ranking that are stored in "FEATURE"_sms as 0,1 (2 for neg framing) to compute SMS choice
#         * [x] Lily-DONE YAY- Store sms choice by factor_set and text_number
#         * [x] Joe-DONE YAY- Retrieve String of that chosen text_number and replace X with total_dichot_adherence_past7
#     * [x] Lily-DONE YAY- Export file once all patients are updated
# * Ranking/Context Features -
#     * [ ] JOE TODO - How to json dump without null values because we don't want these in the model
#     * [ ] JOE TODO - Double checking json dump is working appropriately and looks correct
#     * [ ] Lily/Joe TODO, but kind of done need to just check formatting in general for context features -  How to encode the rank decisions each stepwise rank call to personalizer
#         * ALLSET, IGNORE - Example - How to encode framing = pos in the history rank call
#         * [x] doesn't need to be in its own namespace -  i.e. do we want this as a namespace or is it okay as a free standing variable in the json features list
# * Executability by RA / User friendliness
#     * [x] - Lily done by using Jupyter notebook - Making this more user friendly than a  Command Line
#     * [ ] - JOE TODO / help brainstorm - make jupyter notebook pretty and write a how to document for new non CS person to be able to execute this from Jupyter notebook
#     * [ ] - JOE TODO / help brainstorm - Making this more user friendly than a Jupyter Notebook - to do by doing a main.py executable bash script
#     * [ ] - JOE TODO / help brainstorm - Hooks into Pillsy/RedCap for data retrieval - need check in with constance for pillsy and ellen for redcap
#     * [ ] - JOE TODO / help brainstorm - (probably not feasible) Hooks into SMS Platform to automate text sending - need check in with constance
#     * [ ] - JOE TODO / help brainstorm - how to handle the definite 1 human entered variable of personalizer key - file to direct to or? - maybe as marco/elad
#     * [ ] - Lily/JOE TODO / help - try to break this code in any way possible
#     * [ ] - Lily/JOE TODO / help - debug, unit testing
#     * [ ] - Lily/JOE TODO / help - run it fully several times based in dropbox together
#     * [ ] - Lily/JOE TODO / help - Make a log file that will report high level information from running this like a run summary
#         * elements to include:
#             * start and end time of the run
#             * how many patients were read in from each import statement
#             * how many reward calls were successfull made
#             * how many rank calls were successfull made
#             * any other meta data that will help us debug and ensure this is all working as planned
# 
# 
# 
