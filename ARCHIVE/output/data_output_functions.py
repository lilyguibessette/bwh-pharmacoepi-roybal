import os
import datetime
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from data_classes.Patient import Patient
import pickle

<<<<<<< HEAD
def export_pt_dict_pickle(pt_dict):
    # At the end of the entire run of the program, the patient dictionary is completely saved in pickle format for use
    # for tomorrow's run. It is dated with today's date - i.e. the date the data was generated.
    pickle_filename = str(date.today()) + "_patient_dict" + '.pickle'
=======
def export_pt_dict_pickle(pt_dict, run_time):
    # At the end of the entire run of the program, the patient dictionary is completely saved in pickle format for use
    # for tomorrow's run. It is dated with today's date - i.e. the date the data was generated.
    pickle_filename = str(run_time.date()) + "_patient_dict" + '.pickle'
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
    fp = os.path.join("..", "..", "PatientData", pickle_filename)
    with open(fp, 'wb') as fp:
        pickle.dump(pt_dict, fp)

<<<<<<< HEAD
def export_post_reward_pickle(pt_dict):
    filesave = str(date.today()) + "rewarded_patient_dict" + '.pickle'
=======
def export_post_reward_pickle(pt_dict, run_time):
    filesave = str(run_time.date()) + "rewarded_patient_dict" + '.pickle'
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
    filepath = os.path.join("..", "..", "..", "RewardedPatientData", filesave)
    with open(filepath, 'wb') as fp:
        pickle.dump(pt_dict, fp)

<<<<<<< HEAD
def write_data(pt_dict):
    #WORK IN PROGRESS FOR CONVERTING PICKLE TO CSV FILE FOR HUMAN READABILITY
    new_file = date.today().__str__()
    new_file = "PatientTrialData_" + new_file
    out_file = open(new_file, "w")
    out_file.write('variable headings')

=======
def write_pt_data_csv(pt_dict, run_time):
    # FOR CONVERTING PICKLE TO CSV FILE FOR HUMAN READABILITY
    filesave = str(run_time.date()) + "patient_dict" + '..csv'
    filepath = os.path.join("..", "..", "..", "PatientData", filesave)
    column_values = ["study_id",
           "start_date",
           "last_run_time",
           "trial_day_counter",
           "censor",
           "age",
           "sex",
           "num_years_dm_rx",
           "hba1c",
           "race_white",
           "race_black",
           "race_asian",
           "race_hispanic",
           "race_native",
           "race_pacific",
           "race_other",
           "num_physicians",
           "num_rx",
           "concomitant_insulin_use",
           "automaticity",
           "pt_activation",
           "reason_dm_rx",
           "non_adherence",
           "edu_level",
           "employment_status",
           "marital_status",
           "num_twice_daily_pillsy_meds",
           "pillsy_meds_agi",
           "pillsy_meds_dpp4",
           "pillsy_meds_glp1",
           "pillsy_meds_meglitinide",
           "pillsy_meds_metformin",
           "pillsy_meds_sglt2",
           "pillsy_meds_sulfonylurea",
           "pillsy_meds_thiazolidinedione",
           "num_pillsy_meds",
           "avg_adherence_7day",
           "avg_adherence_3day",
           "avg_adherence_1day",
           "adherence_day1",
           "adherence_day2",
           "adherence_day3",
           "adherence_day4",
           "adherence_day5",
           "adherence_day6",
           "adherence_day7",
           "dichot_adherence_day1",
           "dichot_adherence_day2",
           "dichot_adherence_day3",
           "dichot_adherence_day4",
           "dichot_adherence_day5",
           "dichot_adherence_day6",
           "dichot_adherence_day7",
           "total_dichot_adherence_past7",
           "early_rx_use_before_sms",
           "possibly_disconnected_day1",
           "possibly_disconnected_day2",
           "possibly_disconnected",
           "possibly_disconnected_date",
           "dates_possibly_disconnected",
           "num_dates_possibly_disconnected",
           "num_possibly_disconnected_indicator_true",
           "num_day_since_no_sms",
           "num_day_since_pos_framing",
           "num_day_since_neg_framing",
           "num_day_since_history",
           "num_day_since_social",
           "num_day_since_content",
           "num_day_since_reflective",
           "sms_msg_today",
           "factor_set",
           "text_number",
           "text_message",
           "framing_sms",
           "history_sms",
           "social_sms",
           "content_sms",
           "reflective_sms",
           "quantitative_sms",
           "doctor_sms",
           "lifestyle_sms",
           "response_action_id_framing",
           "response_action_id_history",
           "response_action_id_social",
           "response_action_id_content",
           "response_action_id_reflective",
           "rank_id_framing",
           "rank_id_history",
           "rank_id_social",
           "rank_id_content",
           "rank_id_reflective",
           "reward_value"]
    pt_dict_dataframe = pd.DataFrame(columns=column_values)
>>>>>>> a89090f9422cf1e64bf60e9e9dd30a920db9982f
    for patient in pt_dict:
        new_row = patient.export_to_row()
        pt_dict_dataframe.loc[len(pt_dict_dataframe)] = new_row
    pt_dict_dataframe.to_csv(filepath)
