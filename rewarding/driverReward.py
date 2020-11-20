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
