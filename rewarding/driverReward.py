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
from datetime import datetime
from collections import Counter
import string
import pickle
import json
import os
from datetime import date

def get_reward_update(pt_dict_with_reward):
    reward_filename = str(date.today()) + "_reward_updates" + '.csv'
    reward_filepath = os.path.join("..", "..", "..", "RewardData", reward_filename)

    # Subset updated_pt_dict to what we need for reward calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['reward', 'frame_id', 'history_id', 'social_id', 'content_id', 'reflective_id', 'study_id', 'trial_day_counter']
    reward_updates = pd.DataFrame(columns=column_values)

    for pt, data in pt_dict_with_reward:
        # Reward value, Rank_Id's
        new_row = [data.reward_values, data.rank_id_framing, data.rank_id_history,
                   data.rank_id_social, data.rank_id_content, data.rank_id_reflective,
                   data.study_id, data.trial_day_counter]
        reward_updates.loc[len(reward_updates)] = new_row

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
