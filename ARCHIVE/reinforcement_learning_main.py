# <Dependencies>
import sys
import numpy as np
import pandas as pd
import time
import datetime
from datetime import datetime
import pickle
import json
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials
import datetime, json, os, time, uuid
from datetime import datetime
from actions import get_framing_actions
from actions import get_history_actions
from actions import get_social_actions
from actions import get_content_actions
from actions import get_reflective_actions
import convertPillsy
from patientClass import import_redcap, import_patient_data_pickle

# </Dependencies>



if __name__ == '__main__':
    start_time = time.time()
    start = input("Trial Initiation? Y/N: ")
    redcap_file_path = input("RedCap File Path: ")
    # Example
    #MAC:   /Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/RedCap/Sample REDCap Data_11-11-20.csv
    #PC:    C:\Users\lg436\Dropbox (Partners HealthCare)\SHARED -- REINFORCEMENT LEARNING\RedCap\Sample REDCap Data_11-11-20.csv

    redcap_data = import_redcap(redcap_file_path)
    if start == "N":
        pt_dict_file_path = input("Patient Data File Path: ")
        pt_dict = import_patient_data_pickle(pt_dict_file_path)
        new_pillsy_filepath = input("Pillsy Data File Path: ")
        new_pillsy_data = convertPillsy.import_Pillsy(new_pillsy_filepath)

        #Example
        #MAC:   /Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/Pillsy/PILLSY_Full Sample_CF.csv
        #PC:    C:\Users\lg436\Dropbox (Partners HealthCare)\SHARED -- REINFORCEMENT LEARNING\Pillsy\PILLSY_Full Sample_CF.csv












    old_stdout = sys.stdout
    name = "RL_log" + start_time.__str__() + ".txt"
    log_file = open(name, "w")



    log_file.close()
    sys.stdout = old_stdout
    print("Done.")
