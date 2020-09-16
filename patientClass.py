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


class Patient:
    def __init__(self, P_ID, expdate, EMPI, outcome):
        self.P_ID = P_ID
        self.expdate = expdate
        self.EMPI = EMPI
        self.outcome = outcome
        self.notelist = [] #list of notes from Note class

    def update(self):

 def import_demographics(filepath):
    print("Importing patient data")
    demographics = pd.read_csv(filepath)
    demographics.Age = demographics.Age.astype(int)
    demographics.YearDMRx = demographics.YearDMRx.astype(int)
    return
