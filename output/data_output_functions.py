import os
import datetime
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from data_classes.Patient import Patient
import pickle

def export_pt_dict_pickle(pt_dict):
    # At the end of the entire run of the program, the patient dictionary is completely saved in pickle format for use
    # for tomorrow's run. It is dated with today's date - i.e. the date the data was generated.
    pickle_filename = str(date.today()) + "_patient_dict" + '.pickle'
    fp = os.path.join("..", "..", "PatientData", pickle_filename)
    with open(fp, 'wb') as fp:
        pickle.dump(pt_dict, fp)

def export_reward_data(reward_np_array):
    reward_file_name = str(date.today()) + "_reward_updates" + '.csv'
    fp = os.path.join("..", "..", "..", "RewardData", reward_file_name)
    pd.DataFrame(reward_np_array).to_csv(fp)

def export_post_reward_pickle(pt_dict):
    filesave = str(date.today()) + "rewarded_patient_dict" + '.pickle'
    filepath = os.path.join("..", "..", "..", "RewardedPatientData", filesave)
    with open(filepath, 'wb') as fp:
        pickle.dump(pt_dict, fp)



def write_data(pt_dict):
    #WORK IN PROGRESS FOR CONVERTING PICKLE TO CSV FILE FOR HUMAN READABILITY
    new_file = date.today().__str__()
    new_file = "PatientTrialData_" + new_file
    out_file = open(new_file, "w")
    out_file.write('variable headings')

    for patient in pt_dict:
        out_file.write(patient + '\n')

    out_file.close()