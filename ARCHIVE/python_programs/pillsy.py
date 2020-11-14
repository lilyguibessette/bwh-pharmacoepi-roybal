import pandas as pd
import numpy as np
import sys
import os
import re
import gc
import time
import datetime
from datetime import datetime
from collections import Counter
import string
import pickle
import json

# Imports Pillsy File and Convert to Numpy array
def import_Pillsy(filepath):
    date_cols = ["eventTime"]
    pillsy = pd.read_csv(filepath, sep=',', parse_dates=date_cols)
    pillsy.drop("patientId", axis=1, inplace=True)
    pillsy.drop("lastname",axis=1, inplace=True)
    pillsy.drop("method",axis=1, inplace=True)
    pillsy.drop("platform",axis=1, inplace=True)
    pillsy = pillsy.to_numpy()
    return pillsy




if __name__ == '__main__':
    pt_dict_file_path = input("Patient Data File Path: ")
    pt_dict = import_patient_data_pickle(pt_dict_file_path)
    new_pillsy_filepath = input("Pillsy Data File Path: ")
    new_pillsy_data = import_Pillsy(new_pillsy_filepath)

        #Example
        #MAC:   /Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/Pillsy/PILLSY_Full Sample_CF.csv
        #PC:    C:\Users\lg436\Dropbox (Partners HealthCare)\SHARED -- REINFORCEMENT LEARNING\Pillsy\PILLSY_Full Sample_CF.csv



