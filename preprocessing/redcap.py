import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from data_classes.Patient import Patient
import pickle
from output.data_output_functions import export_pt_dict_pickle
from input.data_input_functions import import_redcap


def get_redcap_study_ids(redcap):
    # Subsets the redcap data into the record_id column
    study_ids_redcap = redcap['record_id']
    # Drops duplicate id's so we have a succinct list (not particularly necessary)
    unique_study_ids_redcap = study_ids_redcap.drop_duplicates()
    # convert the record id's into a list to return
    unique_study_ids_list_redcap = unique_study_ids_redcap.values.tolist()
    # returns a list of the unique record_id's in the redcap data
    return unique_study_ids_list_redcap

def update_patient_dict_redcap(redcap, pt_dict, run_time):
    # Get a list of the patient record_id's in the REDCap dataset
    unique_study_ids_list_redcap = get_redcap_study_ids(redcap)
    # Get a list of current patients as pt_dict_keys = patients record_id's that we already have in our pickle/patient dictionary
    pt_dict_keys = list(pt_dict.keys())
    # Instantiate an empty dictionary to add to
    updated_pt_dict = {}
    # For each patient in the list of record_id's that exists in the redcap data
    for record_id in unique_study_ids_list_redcap:
        # We get the patient's row of data in redcap
        row = redcap.loc[redcap['record_id'] == record_id] # pick first row #TODO
        # TODO - have Joe think about what if for whatever reason there were multiple rows of data in redcap with the same record_id => same patient
        # Need this to make sure that making a new Patient/Calling on the row[]'s that we will get one value back and not 2

        # If the patient doesn't already exist in our patient dictionary and they don't have a true censor indicator:
        if record_id not in pt_dict_keys and int(row['censor']) != 1:
            # Create a new rough draft type of patient object from the REDCap data
            # This new patient has the counter set to 0 on day that they're beginning follow up in the study.
            new_patient = Patient(str(record_id),
                                  row['start_date'].values[0],
                                  run_time,
                                  0,
                                  False,
                                  int(row['age'].values[0]),
                                  int(row['sex']),
                                  int(row['num_years_dm_rx']),
                                  int(row['hba1c']),
                                  int(row['race___1']),
                                  int(row['race___2']),
                                  int(row['race___3']),
                                  int(row['race___4']),
                                  int(row['race___5']),
                                  int(row['race___6']),
                                  int(row['race___7']),
                                  int(row['num_physicians']),
                                  int(row['num_rx']),
                                  int(row['concomitant_insulin_use']),
                                  int(row['automaticity']),
                                  int(row['pt_activation']),
                                  int(row['reason_dm_rx']),
                                  int(row['non_adherence']),
                                  int(row['edu_level']),
                                  int(row['employment_status']),
                                  int(row['marital_status']),
                                  int(row['num_twice_daily_pillsy_meds']),
                                  int(row['pillsy_meds___1']),
                                  int(row['pillsy_meds___2']),
                                  int(row['pillsy_meds___3']),
                                  int(row['pillsy_meds___4']),
                                  int(row['pillsy_meds___5']),
                                  int(row['pillsy_meds___6']),
                                  int(row['pillsy_meds___7']),
                                  int(row['pillsy_meds___8']),
                                  int(row['bottles']),
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

            # TODO - finish convert_redcap_input_vars() function in Patient Class once Julie approves/confirms
            # NEED TO ENSURE CATEGORIES COMING IN ARE RECODED TO APPROPRIATE STRINGS
            # i.e. CATEGORY from redcap = 1 => age 18-25 (rough example) ->
            # shouldn't be continuous, needs to be string to become categorical to Personalizer

            # Have the new patient object 'clean' itself to properly formatted data
            #   - i.e. Converts function has patient convert from redcap input values to string types for categorical variables etc.
            new_patient.convert_redcap_input_vars()
            # Add this cleaned new patient to our new patient dictionary
            updated_pt_dict[record_id] = new_patient
        else:
            # Then the patient already exists in our patient dictionary
            # We retrieve their data from the patient_dictionary using their record_id
            updated_patient = pt_dict.get(record_id)
            # Using the get() method for dictionaries will not raise a KeyError if the record_id doesn't exist,
            # but it will return None, so we make sure it finds a patient in our dictionary
            #TODO if updated_patient is None, then need to figure out how to handle but this is a rare possibility and seems okay to just drop them
            if updated_patient != None:
                #TODO double check with Julie they're getting censored at day 180

                # If the patient doesn't have a true censoring indicator and hasn't met the 180 end of follow up window - i.e. maximum time reached = 180 days
                if int(row['censor']) != 1 and updated_patient.trial_day_counter < 180:

                    #TODO make an exported list to appended to the record_ids that are getting censored here
                    # Then we'll update to the current values in the REDCap dataset for their Pillsy baseline information
                    updated_patient.update_redcap_pillsy_vars(int(row['num_twice_daily_pillsy_meds']),
                                                          int(row['pillsy_meds___1']),
                                                          int(row['pillsy_meds___2']),
                                                          int(row['pillsy_meds___3']),
                                                          int(row['pillsy_meds___4']),
                                                          int(row['pillsy_meds___5']),
                                                          int(row['pillsy_meds___6']),
                                                          int(row['pillsy_meds___7']),
                                                          int(row['pillsy_meds___8']),
                                                              int(row['bottles']))
                    # Then we'll add this patient to our patient dictionary with their record_id
                    updated_pt_dict[record_id] = updated_patient
    # We return the updated patient dictionary that takes into account the new patients/new patient data from REDCap and
    # the historical data we have for existing patients that are enrolled in the trial and actively receiving messages.
    return updated_pt_dict


# Tseting
# if __name__ == '__main__':
# def redcap_testing():
#     pt_dict = {}
#     redcap_data = import_redcap(
#         "/Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/RedCap/Sample REDCap Data_11-11-20.csv")
#     unique_study_ids_list_redcap = get_redcap_study_ids(redcap_data)
#     pt_dict_redcap = update_patient_dict_redcap(unique_study_ids_list_redcap, redcap_data, pt_dict)
#     for pt, data in pt_dict_redcap.items():
#         print("\n This is the record_id", pt)
#         print("This is the start date ", data.start_date)
#         print("checking the counter ", data.trial_day_counter)
#         print("checking the age", data.age)
#         print("checking race_black", data.race_black)
#         print(data.last_run_time, ",", data.start_date, ",", str(data.last_run_time), ",", str(data.start_date), ",",
#               str(data.age), ",", str(data.race_black), ",", str(data.dichot_adherence_day1), ",",
#               str(data.response_action_id_framing))
#         print(pt, ",", data.last_run_time, ",", data.start_date, ", age:", data.age, ",", data.race_black, ",",
#               data.dichot_adherence_day1, ",", data.response_action_id_framing)
#     export_pt_dict_pickle(pt_dict_redcap)
