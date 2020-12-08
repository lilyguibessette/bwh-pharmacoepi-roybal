import os
import pandas as pd

def import_pt_data(run_time):
    import_date = (run_time - pd.Timedelta("1 day")).date()
    # Imports Pillsy pill taking history as a pandas data frame from a CSV

    pt_data_filename = str(import_date) + "_pt_data" + '.csv'
    fp = os.path.join("..",  "PatientData", pt_data_filename)
    date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
#     data_types = [{"record_id":int64},
#                   {"trial_day_counter":int64},
#                   {"censor":int64},
#                   {"age":str},
#                   {"sex":str},
#                   {"num_years_dm_rx":str},
#                   {"hba1c":str},
#                   {"race_white":int64},
#                   {"race_black":int64},
#                   {"race_asian":int64},
#                   {"race_hispanic":int64},
#                   {"race_other":int64},
#                   {"num_physicians":str},
#                   {"num_rx":str},
#                   {"concomitant_insulin_use":int64},
#                   {"automaticity":str},
#                   {"pt_activation":str},
#                   {"reason_dm_rx":str},
#                   {"non_adherence":str},
#                   {"edu_level":str},
#                   {"employment_status":str},
#                   {"marital_status":str},
#                   {"num_twice_daily_pillsy_meds":int64},
#                   {"pillsy_meds_agi":int64},
#                   {"pillsy_meds_dpp4":int64},
#                   {"pillsy_meds_glp1":int64},
#                   {"pillsy_meds_meglitinide":int64},
#                   {"pillsy_meds_metformin":int64},
#                   {"pillsy_meds_sglt2":int64},
#                   {"pillsy_meds_sulfonylurea":int64},
#                   {"pillsy_meds_thiazolidinedione":int64},
#                   {"num_pillsy_meds":int64},
#                   {"avg_adherence_7day":float64},
#                   {"avg_adherence_3day":float64},
#                   {"avg_adherence_1day":float64},
#                   {"adherence_day1":float64},
#                   {"adherence_day2":float64},
#                   {"adherence_day3":float64},
#                   {"adherence_day4":float64},
#                   {"adherence_day5":float64},
#                   {"adherence_day6":float64},
#                   {"adherence_day7":float64},
#                   {"dichot_adherence_day1":int64},
#                   {"dichot_adherence_day2":int64},
#                   {"dichot_adherence_day3":int64},
#                   {"dichot_adherence_day4":int64},
#                   {"dichot_adherence_day5":int64},
#                   {"dichot_adherence_day6":int64},
#                   {"dichot_adherence_day7":int64},
#                   {"total_dichot_adherence_past7":int64},
#                   {"early_rx_use":float64},
#                   {"disconnectedness":int64},
#                   {"possibly_disconnected_day1":bool},
#                   {"possibly_disconnected_day2":bool},
#                   {"possibly_disconnected":bool},
#                   {"dates_possibly_disconnected":list()},
#                   {"num_dates_possibly_disconnected":int64},
#                   {"num_possibly_disconnected_indicator_true":int64},
#                   {"num_day_since_no_sms":int64},
#                   {"num_day_since_pos_framing":int64},
#                   {"num_day_since_neg_framing":int64},
#                   {"num_day_since_history":int64},
#                   {"num_day_since_social":int64},
#                   {"num_day_since_content":int64},
#                   {"num_day_since_reflective":int64},
#                   {"sms_msg_today":str},
#                   {"factor_set":int64},
#                   {"text_number":int64},
#                   {"text_message":str},
#                   {"framing_sms":int64},
#                   {"history_sms":int64},
#                   {"social_sms":int64},
#                   {"content_sms":int64},
#                   {"reflective_sms":int64},
#                   {"quantitative_sms":int64},
#                   {"doctor_sms":int64},
#                   {"lifestyle_sms":int64},
#                   {"response_action_id_framing":str},
#                   {"response_action_id_history":str},
#                   {"response_action_id_social":str},
#                   {"response_action_id_content":str},
#                   {"response_action_id_reflective":str},
#                   {"flag_send_reward_value_t0":bool},
#                   {"reward_value_t0":float64},
#                   {"rank_id_framing_t0":str},
#                   {"rank_id_history_t0":str},
#                   {"rank_id_social_t0":str},
#                   {"rank_id_content_t0":str},
#                   {"rank_id_reflective_t0":str},
#                   {"flag_send_reward_value_t1":bool},
#                   {"reward_value_t1":float64},
#                   {"rank_id_framing_t1":str},
#                   {"rank_id_history_t1":str},
#                   {"rank_id_social_t1":str},
#                   {"rank_id_content_t1":str},
#                   {"rank_id_reflective_t1":str},
#                   {"flag_send_reward_value_t2":bool},
#                   {"reward_value_t2":float64},
#                   {"rank_id_framing_t2":str},
#                   {"rank_id_history_t2":str},
#                   {"rank_id_social_t2":str},
#                   {"rank_id_content_t2":str},
#                   {"rank_id_reflective_t2":str}]
    try:
        pt_data = pd.read_csv(fp, sep=',', parse_dates=date_cols) #, dtype=data_types)
    except FileNotFoundError as fnfe:
        print("in patient_data.py, in import_pt_data")
        print("fp file not found, fp = {}".format(os.path.abspath(fp)))
        print("error = {}".format(fnfe))
        pt_data = new_empty_pt_data()
        return pt_data
    return pt_data


def new_empty_pt_data():
    fp = os.path.join("..", "PatientData", "empty_start.csv")
    date_cols = ["start_date", "censor_date", "possibly_disconnected_date"]
    pt_data = pd.read_csv(fp, sep=',', header=0, parse_dates=date_cols)
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
    pt_data.to_csv(filepath, index=False)


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