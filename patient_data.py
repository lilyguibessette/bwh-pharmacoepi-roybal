import os
import pandas as pd

def import_pt_data(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    # Imports Pillsy pill taking history as a pandas data frame from a CSV

    pt_data_filename = str(import_date) + "_pt_data" + '.csv'
    fp = os.path.join("..",  "PatientData", pt_data_filename)
    date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    except FileNotFoundError:
        fp = os.path.join("..", "PatientData", "empty_start.csv")
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
        return pt_data
    return pt_data


def new_empty_pt_data():
    fp = os.path.join("..", "PatientData", "empty_start.csv")
    date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
    pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    return pt_data

def export_pt_data(pt_data, runtime, purpose):
    filesave = str(runtime.date()) + "_pt_data" + '.csv'
    if purpose.lower() == "reward":
        filepath = os.path.join("..",  "RewardLog", filesave)
    elif purpose.lower() == "rank":
        filepath = os.path.join("..",  "RankLog", filesave)
    elif purpose.lower() == "final":
        filepath = os.path.join("..",  "PatientData", filesave)
    else:
        filepath = os.path.join("..",  "Trash", filesave)
    pt_data.to_csv(filepath)


def get_study_ids(pt_data):
    try:
    # Subsets the firstname column to find the unique study_id's available in the Pillsy data to update adherence
        study_ids_df = pt_data['record_id'].copy()
        unique_study_ids_df = study_ids_df.drop_duplicates()
        unique_study_ids_list = unique_study_ids_df.values.tolist()
    except ValueError:
        unique_study_ids_list = []
    except TypeError:
        unique_study_ids_list = []
        
    return unique_study_ids_list