import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil import parser, tz
import pickle
import os
import re


def import_redcap(run_time):
    import_date = run_time.date()
    # Imports REDCap patients that are enrolling on an ongoing basis as a pandas data frame from a CSV
    redcap_filepath = str(import_date) + "_redcap" + '.csv'
    fp = os.path.join("..", "..", "REDCap", redcap_filepath)
    date_cols = ["start_date"]
    # Reads in the csv file into a pandas data frame and ensures that the date_cols are imported as datetime.datetime objects
    # TODO potentially need to be careful here due to use of the data in redcap.py -> might want to ensure record_id column is a string, currently I think it defaults to an int - might bee fine to keep int
    redcap = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    redcap = redcap_vars_converter(redcap)
    # Returns the pandas dataframe of REDCap patient data that is read in
    # Note: The REDCap data does not contain observed feedback.
    # Hence why we do not overwrite our previous patient dictionary based on this data.
    # This is used to update patient dictionary data about:
    #   -   Whether patients are censored (i.e. due to death, consent withdrawal,
    #   -   Changes in Pillsy medications that a patient is taking
    #   -   Add entirely new patients initiating in the study to our patient dictionary by creating new patient objects
    return redcap


# For a DataFrame a dict can specify that different values should be replaced in different columns. For example, {'a': 1, 'b': 'z'} looks for the value 1 in column ‘a’ and the value ‘z’ in column ‘b’ and replaces these values with whatever is specified in value. The value parameter should not be None in this case. You can treat this as a special case of passing two lists except that you are specifying the column to search in.

def redcap_vars_converter(redcap_df):
    # Tested
    redcap_df = redcap_df.replace({'age': 1}, "18-34")
    redcap_df = redcap_df.replace({'age': 2}, "35-44")
    redcap_df = redcap_df.replace({'age': 3}, "45-54")
    redcap_df = redcap_df.replace({'age': 4}, "55-64")
    redcap_df = redcap_df.replace({'age': 5}, "65-74")
    redcap_df = redcap_df.replace({'age': 6}, "75-84")
    redcap_df = redcap_df.replace({'sex': 1}, "F")
    redcap_df = redcap_df.replace({'sex': 2}, "M")
    redcap_df = redcap_df.replace({'sex': 0}, "Not listed")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 1}, "0")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 2}, "1-2")
    redcap_df = redcap_df.replace({'num_years_dm_rx': 3}, "3-4")  # TODO
    redcap_df = redcap_df.replace({'num_years_dm_rx': 4}, "5+")
    redcap_df = redcap_df.replace({'hba1c': 1}, "7.5-8.0")
    redcap_df = redcap_df.replace({'hba1c': 2}, "8.1-8.9")
    redcap_df = redcap_df.replace({'hba1c': 3}, "9.0-9.9")
    redcap_df = redcap_df.replace({'hba1c': 4}, "10+")
    redcap_df = redcap_df.replace({'num_physicians': 1}, "1")
    redcap_df = redcap_df.replace({'num_physicians': 2}, "2-3")
    redcap_df = redcap_df.replace({'num_physicians': 3}, "4+")  # fixed
    redcap_df = redcap_df.replace({'num_rx': 1}, "1")
    redcap_df = redcap_df.replace({'num_rx': 2}, "2-4")
    redcap_df = redcap_df.replace({'num_rx': 3}, "5-9")
    redcap_df = redcap_df.replace({'num_rx': 4}, "10+")
    redcap_df = redcap_df.replace({'automaticity': 0}, "0")
    redcap_df = redcap_df.replace({'automaticity': 1}, "1")
    redcap_df = redcap_df.replace({'automaticity': 2}, "2-3")
    redcap_df = redcap_df.replace({'automaticity': 3}, "4")
    redcap_df = redcap_df.replace({'pt_activation': 1}, "yes")
    redcap_df = redcap_df.replace({'pt_activation': 2}, "most")
    redcap_df = redcap_df.replace({'pt_activation': 3}, "no")
    redcap_df = redcap_df.replace({'reason_dm_rx': 1}, "Supposed to")
    redcap_df = redcap_df.replace({'reason_dm_rx': 2}, "Own good")
    redcap_df = redcap_df.replace({'reason_dm_rx': 3}, "No choice")
    redcap_df = redcap_df.replace({'reason_dm_rx': 4}, "Feel good")
    redcap_df = redcap_df.replace({'reason_dm_rx': 5}, "Important")
    redcap_df = redcap_df.replace({'non_adherence': 0}, "0")
    redcap_df = redcap_df.replace({'non_adherence': 1}, "1")
    redcap_df = redcap_df.replace({'non_adherence': 2}, "2-3")
    redcap_df = redcap_df.replace({'non_adherence': 3}, "4-6")
    redcap_df = redcap_df.replace({'non_adherence': 4}, "7+")
    redcap_df = redcap_df.replace({'edu_level': 1}, "HS or below/HS grad")
    redcap_df = redcap_df.replace({'edu_level': 2}, "Some college")
    redcap_df = redcap_df.replace({'edu_level': 3}, "College grad/Postgrad")
    redcap_df = redcap_df.replace({'edu_level': 4}, "other")
    redcap_df = redcap_df.replace({'employment_status': 1}, "Employed")
    redcap_df = redcap_df.replace({'employment_status': 2}, "Retired/Other")
    redcap_df = redcap_df.replace({'marital_status': 1}, "Married/partner")
    redcap_df = redcap_df.replace({'marital_status': 2}, "window/divorced/single/other")
    return redcap_df


def update_pt_data_with_redcap(redcap_data, pt_data, run_time):
    # TODO Joe - can you check this function thats purpose is to just add the redcap data to the pt_data for new patients and for existing patients updatee their existing censor and pillsy related info with the new redcap info
    unique_study_ids_list_redcap = get_unique_study_ids(redcap_data)
    unique_study_ids_list_pt_data = get_unique_study_ids(pt_data)

    # Updating existing patients
    for index, patient in pt_data.iterrows():
        record_id = patient["record_id"]
        row = redcap_data[redcap_data["record_id"] == record_id]
        # need to make sure via iterating it updates this data in the df
        patient["censor"] = row["censor"]
        patient["num_twice_daily_pillsy_meds"] = row["num_twice_daily_pillsy_meds"]
        patient["pillsy_meds_agi"] = row["pillsy_meds___1"]
        patient["pillsy_meds_dpp4"] = row["pillsy_meds___2"]
        patient["pillsy_meds_glp1"] = row["pillsy_meds___3"]
        patient["pillsy_meds_meglitinide"] = row["pillsy_meds___4"]
        patient["pillsy_meds_metformin"] = row["pillsy_meds___5"]
        patient["pillsy_meds_sglt2"] = row["pillsy_meds___6"]
        patient["pillsy_meds_sulfonylurea"] = row["pillsy_meds___7"]
        patient["pillsy_meds_thiazolidinedione"] = row["pillsy_meds___8"]
        patient["num_pillsy_meds"] = row["bottles"]
        # shift these values for the next rank to store t0 values
        patient["reward_value_t1"] = patient["reward_value_t0"]
        patient["rank_id_framing_t1"] = patient["rank_id_framing_t0"]
        patient["rank_id_history_t1"] = patient["rank_id_history_t0"]
        patient["rank_id_social_t1"] = patient["rank_id_social_t0"]
        patient["rank_id_content_t1"] = patient["rank_id_content_t0"]
        patient["rank_id_reflective_t1"] = patient["rank_id_reflective_t0"]
        patient["reward_value_t2"] = patient["reward_value_t1"]
        patient["rank_id_framing_t2"] = patient["rank_id_framing_t1"]
        patient["rank_id_history_t2"] = patient["rank_id_history_t1"]
        patient["rank_id_social_t2"] = patient["rank_id_social_t1"]
        patient["rank_id_content_t2"] = patient["rank_id_content_t1"]
        patient["rank_id_reflective_t2"] = patient["rank_id_reflective_t1"]

    # Adding new patients
    for id in unique_study_ids_list_redcap:
        if id not in unique_study_ids_list_pt_data:
            redcap_row = redcap_data[redcap_data['record_id'] == id]
            # Collapses race to other
            if redcap_row["race___5"] == 1 or redcap_row["race___6"] == 1 or redcap_row["race___7"] == 1:
                race_other = 1
            else:
                race_other = 0
            new_row = pd.Series(pt_data={'record_id': id,
                                         'trial_day_counter': 0,
                                         'age': redcap_row["age"],
                                         'sex': redcap_row["sex"],
                                         'num_years_dm_rx': redcap_row["num_years_dm_rx"],
                                         'hba1c': redcap_row["hba1c"],
                                         'race_white': int(redcap_row["race___1"]),
                                         'race_black': redcap_row["race___2"],
                                         'race_asian': redcap_row["race___3"],
                                         'race_hispanic': redcap_row["race___4"],
                                         'race_other': race_other,
                                         'num_physicians': redcap_row["num_physicians"],
                                         'num_rx': redcap_row["num_rx"],
                                         'concomitant_insulin_use': redcap_row["concomitant_insulin_use"],
                                         'automaticity': redcap_row["automaticity"],
                                         'pt_activation': redcap_row["pt_activation"],
                                         'reason_dm_rx': redcap_row["reason_dm_rx"],
                                         'non_adherence': redcap_row["non_adherence"],
                                         'edu_level': redcap_row["edu_level"],
                                         'employment_status': redcap_row["employment_status"],
                                         'marital_status': redcap_row["marital_status"],
                                         'pillsy_meds_agi': redcap_row["pillsy_meds___1"],
                                         'pillsy_meds_dpp4': redcap_row["pillsy_meds___2"],
                                         'pillsy_meds_glp1': redcap_row["pillsy_meds___3"],
                                         'pillsy_meds_meglitinide': redcap_row["pillsy_meds___4"],
                                         'pillsy_meds_metformin': redcap_row["pillsy_meds___5"],
                                         'pillsy_meds_sglt2': redcap_row["pillsy_meds___6"],
                                         'pillsy_meds_sulfonylurea': redcap_row["pillsy_meds___7"],
                                         'pillsy_meds_thiazolidinedione': redcap_row["pillsy_meds___8"],
                                         'num_pillsy_meds': redcap_row["bottles"],
                                         'start_date': redcap_row["start_date"],
                                         'num_twice_daily_pillsy_meds': redcap_row["num_twice_daily_pillsy_meds"],
                                         'censor': redcap_row["censor"]}, name='new')
            pt_data = pt_data.append(new_row)

    return pt_data


def get_unique_study_ids(df):
    # Subsets the redcap data into the record_id column
    study_ids = df['record_id'].copy()
    # Drops duplicate id's so we have a succinct list (not particularly necessary)
    unique_study_ids = study_ids.drop_duplicates()
    # convert the record id's into a list to return
    unique_study_ids_list = unique_study_ids.values.tolist()
    # returns a list of the unique record_id's in the redcap data
    return unique_study_ids_list
