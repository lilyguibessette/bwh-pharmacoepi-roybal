import os
import pandas as pd

def import_pt_data(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    # Imports Pillsy pill taking history as a pandas data frame from a CSV

    pt_data_filename = str(import_date) + "_pt_data" + '.csv'
    fp = os.path.join("..", "..", "PatientData", pt_data_filename)
    date_cols = ["start_date"]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    except FileNotFoundError:
        return None
    return pt_data


def export_pt_data(pt_data, runtime, purpose):
    filesave = str(runtime.date()) + "_pt_data_" + purpose.lower() + '.csv'
    if purpose.lower() == "reward":
        filepath = os.path.join("..", "..", "RewardLog", filesave)
    if purpose.lower() == "rank":
        filepath = os.path.join("..", "..", "RankLog", filesave)
    if purpose.lower() == "final":
        filepath = os.path.join("..", "..", "PatientData", filesave)
    pt_data.to_csv(filepath)