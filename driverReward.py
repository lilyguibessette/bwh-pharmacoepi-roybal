# <reward>
import sys
import time
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankRequest
from msrest.authentication import CognitiveServicesCredentials
import pandas as pd
import numpy as np
import math
import time
from datetime import datetime, date, timedelta
import pytz
from collections import Counter
import string
import pickle
import json
import os
from datetime import date

def get_reward_update(pt_data, run_time):
    reward_filename = str(run_time.date()) + "_reward_updates" + '.csv'
    reward_filepath = os.path.join("..", "RewardData", reward_filename)
    today = run_time.date()
    two_day_ago = (run_time - timedelta(days=2)).date()
    yesterday = (run_time - timedelta(days=1)).date()


    # Subset updated_pt_dict to what we need for reward calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['reward', 'frame_id', 'history_id', 'social_id', 'content_id', 'reflective_id', 'record_id', 'trial_day_counter']
    reward_updates = pd.DataFrame(columns=column_values)

    for pt,data_row in pt_data.iterrows():
        # Reward value, Rank_Id's
        if(data_row["flag_send_reward_value_t0"] == True and data_row["censor_date"] >= today):
            reward_row_t0 = [data_row["reward_value_t0"], data_row["rank_id_framing_t0"], data_row["rank_id_history_t0"],
                       data_row["rank_id_social_t0"], data_row["rank_id_content_t0"], data_row["rank_id_reflective_t0"],
                       data_row["record_id"], data_row["trial_day_counter"]]
            reward_updates.loc[len(reward_updates)] = reward_row_t0
        if(data_row["flag_send_reward_value_t1"] == True and data_row["censor_date"] >= yesterday):
            reward_row_t1 = [data_row["reward_value_t1"], data_row["rank_id_framing_t1"], data_row["rank_id_history_t1"],
                       data_row["rank_id_social_t1"], data_row["rank_id_content_t1"], data_row["rank_id_reflective_t1"],
                       data_row["record_id"], data_row["trial_day_counter"]-1]
            reward_updates.loc[len(reward_updates)] = reward_row_t1
        if(data_row["flag_send_reward_value_t2"] == True and data_row["censor_date"]  >= two_day_ago):
            reward_row_t2 = [data_row["reward_value_t2"], data_row["rank_id_framing_t2"], data_row["rank_id_history_t2"],
                       data_row["rank_id_social_t2"], data_row["rank_id_content_t2"], data_row["rank_id_reflective_t2"],
                       data_row["record_id"], data_row["trial_day_counter"]-2]
            reward_updates.loc[len(reward_updates)] = reward_row_t2
    # Write csv as a log for what we're sending to Personalizer
    reward_updates.to_csv(reward_filepath)
    reward_updates = reward_updates.to_numpy()
    return reward_updates


def send_rewards(reward_updates, client):
    # column_values = ['reward', '
    #   frame_id', 'history_id', 'social_id', 'content_id', 'reflective_id',
    #   'study_id', 'trial_day_counter']
    for i in range(0,len(reward_updates)):
        row = reward_updates[i, :]
        reward_val = row[0]
        for j in range(1,6):
            #print("reward_val: ", reward_val)
            #print("event_id: ", row[j])
            client.events.reward(event_id=row[j], value=reward_val)
