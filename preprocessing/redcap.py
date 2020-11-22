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
            patient = Patient(str(record_id),
                              row['start_date'],
                              date.today(),
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
            pt_dict[record_id] = patient
        else:
            updated_patient = pt_dict[record_id]
            updated_patient.update_redcap_pillsy_vars(num_twice_daily_pillsy_meds, pillsy_meds_agi, pillsy_meds_dpp4, pillsy_meds_glp1, pillsy_meds_meglitinide, pillsy_meds_metformin, pillsy_meds_sglt2, pillsy_meds_sulfonylurea, pillsy_meds_thiazolidinedione)
            pt_dict.update_pt_ob

    return pt_dict


#Tseting
#if __name__ == '__main__':
def redcap_testing():
    pt_dict = {}
    redcap_data = import_redcap("/Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/RedCap/Sample REDCap Data_11-11-20.csv")
    unique_study_ids_list_redcap = get_redcap_study_ids(redcap_data)
    pt_dict_redcap = compare_existing_for_new_ids(unique_study_ids_list_redcap, redcap_data, pt_dict)
    for pt, data in pt_dict_redcap.items():
        print(pt,"\n", data,"\n", data.current_date, "\n",data.start_date,"\n", str(data.race_black),"\n", str(data.dichot_adherence_day1), "\n",str(data.response_action_id_framing))
    export_pt_dict_pickle(pt_dict_redcap)
