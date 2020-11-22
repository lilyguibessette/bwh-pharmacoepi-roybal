import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from data_classes.Patient import Patient
import pickle
from output.data_output_functions import export_pt_dict_pickle
from input.data_input_functions import import_redcap


def get_redcap_study_ids(redcap):
    # Subsets the firstname column to find the unique study_id's available in the Pillsy data to update adherence
    study_ids_redcap = redcap['record_id']
    unique_study_ids_redcap = study_ids_redcap.drop_duplicates()
    unique_study_ids_list_redcap = unique_study_ids_redcap.values.tolist()
    return unique_study_ids_list_redcap

### CENSORING ISSUE HOW WILL THAT COME INTO THE DATA
def update_patient_dict_redcap(unique_study_ids_list_redcap, redcap, pt_dict):
    pt_dict_keys = list(pt_dict.keys())
    for record_id in unique_study_ids_list_redcap:
        row = redcap.loc[redcap['record_id'] == record_id]
        if record_id not in pt_dict_keys:
            #TODO
            # NEED TO ENSURE CATEGORIES COMING IN ARE RECODED TO APPROPRIATE STRINGS
            # i.e. CATEGORY from redcap = 1 => age 18-25 (rough example) ->
            # shouldn't be continuous, needs to be string to become categorical to personalizer
            new_patient = Patient(str(record_id),
                              row['start_date'],
                              datetime.now(),
                              0,
                              False,
                              row['age'],
                              row['sex'],
                              row['num_years_dm_rx'],
                              row['hba1c'],
                              row['race___1'],
                              row['race___2'],
                              row['race___3'],
                              row['race___4'],
                              row['race___5'],
                              row['race___6'],
                              row['race___7'],
                              row['num_physicians'],
                              row['num_rx'],
                              row['concomitant_insulin_use'],
                              row['automaticity'],
                              row['pt_activation'],
                              row['reason_dm_rx'],
                              row['non_adherence'],
                              row['edu_level'],
                              row['employment_status'],
                              row['marital_status'],
                              row['num_twice_daily_pillsy_meds'],
                              row['pillsy_meds___1'],
                              row['pillsy_meds___2'],
                              row['pillsy_meds___3'],
                              row['pillsy_meds___4'],
                              row['pillsy_meds___5'],
                              row['pillsy_meds___6'],
                              row['pillsy_meds___7'],
                              row['pillsy_meds___8'],
                              #row['num_pillsy_meds'],
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              False,
                              False,
                              False,
                              None,
                              None,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              None,
                              None,
                              None,  # text_number,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              None,
                              0)
            # convert function from input values to string type
            # update patient variables
            pt_dict[record_id] = new_patient
        else:
            updated_patient = pt_dict[record_id]
            updated_patient.update_redcap_pillsy_vars(row['num_twice_daily_pillsy_meds'],
                              row['pillsy_meds___1'],
                              row['pillsy_meds___2'],
                              row['pillsy_meds___3'],
                              row['pillsy_meds___4'],
                              row['pillsy_meds___5'],
                              row['pillsy_meds___6'],
                              row['pillsy_meds___7'],
                              row['pillsy_meds___8'])
            pt_dict[record_id] = updated_patient

    return pt_dict


#Tseting
if __name__ == '__main__':
#def redcap_testing():
    pt_dict = {}
    redcap_data = import_redcap("/Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/RedCap/Sample REDCap Data_11-11-20.csv")
    unique_study_ids_list_redcap = get_redcap_study_ids(redcap_data)
    pt_dict_redcap = update_patient_dict_redcap(unique_study_ids_list_redcap, redcap_data, pt_dict)
    for pt, data in pt_dict_redcap.items():
        print(pt,",",data.last_run_time, ",",data.start_date,",", str(data.last_run_time), ",",str(data.start_date),",", str(data.race_black),",", str(data.dichot_adherence_day1), ",",str(data.response_action_id_framing))
        print("\n", pt, ",", data.last_run_time, ",", data.start_date, ",",  data.race_black, ",", data.dichot_adherence_day1, ",", data.response_action_id_framing)
    export_pt_dict_pickle(pt_dict_redcap)
