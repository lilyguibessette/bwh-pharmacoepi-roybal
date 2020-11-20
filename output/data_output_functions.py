
import os
import datetime
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from data_classes.Patient import Patient
import pickle

def export_reward_data(reward_np_array):
    #WORK IN PROGRESS
    mac_path = "~/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/Reward_Data/"
    pc_path = R"C:\Users\$USERNAME\Dropbox (Partners HealthCare)\SHARED -- REINFORCEMENT LEARNING\Reward_Data"
    path = check_mac_or_pc(mac_path, pc_path)
    path = path + ""
    full_path = os.path.expanduser(path)
    pd.DataFrame(reward_np_array).to_csv("path/to/file.csv")

def check_mac_or_pc(mac_or_pc, mac_path,pc_path):
    #WORK IN PROGRESS
    if mac_or_pc == False: # Mac
        path = mac_path
    elif mac_or_pc == True: # PC
        path = pc_path +"\\"
    else:
        path = ""
        print("Error: Invalid computer system type.")
    return path

def export_pt_dict_pickle(pt_dict):
    filesave = date.today().__str__() + "_patient_dict" + '.pickle'
    with open(filesave, 'wb') as fp:
        pickle.dump(pt_dict, fp)

def export_post_reward_pickle(pt_dict):
    filesave = date.today().__str__() + "rewarded_patient_dict" + '.pickle'
    with open(filesave, 'wb') as fp:
        pickle.dump(pt_dict, fp)

def export_post_rank_pickle(pt_dict):
    filesave = date.today().__str__() + "ranked_patient_dict" + '.pickle'
    with open(filesave, 'wb') as fp:
        pickle.dump(pt_dict, fp)

def write_data(pt_dict):
    #WORK IN PROGRESS
    new_file = date.today().__str__()
    new_file = "PatientTrialData_" + new_file
    out_file = open(new_file, "w")
    out_file.write('variable headings')

    for patient in pt_dict:
        out_file.write(patient + '\n')

    out_file.close()