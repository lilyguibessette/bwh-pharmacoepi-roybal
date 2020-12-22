# <Dependencies>
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankRequest
from msrest.authentication import CognitiveServicesCredentials
from Actions import get_framing_actions, get_history_actions, get_social_actions, get_content_actions, get_reflective_actions
# from data_classes.Patient import Patient
# import data_classes.ContextFeatures
from datetime import datetime, date, timedelta
import pytz
import os
import pandas as pd

from exe_functions import build_path


def write_sms_history(pt_data, run_time):
    fp = build_path("000_SMS_TO_SEND", str(run_time.date()) + "_sms_history.csv")
    # Subset updated_pt_dict to what we need for reward calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['record_id','sms_msg_today', 'factor_set', 'text_number',  'trial_day_counter','censor_date']
    sms_history_dataframe = pd.DataFrame(columns=column_values)

    for pt, data in pt_data.iterrows():
        # Reward value, Rank_Id's
        sms_history_dataframe.loc[len(sms_history_dataframe)] = [data["record_id"], data["sms_msg_today"], data["factor_set"], data["text_number"], data["trial_day_counter"], str(data["censor_date"])]
    # Writes CSV for RA to send text messages.
    sms_history_dataframe.to_csv(fp, index=False)

def run_ranking(patient, client, run_time):
    """Send rank calls to Personalizer and update corresponding patient variables.

    1. Shift rank ids
    2. Make rank calls (framing, history, social, content, reflective)
        a. construct event_id
        b. get context features
        c. get actions
        d. call RankRequest
        e. get response, convert to int
        f. update patient var
    3. Update patient num days since rank calls
    4. Update appropriate sms vars in patient row
    """
    patient= shift_t0_t1_rank_ids(patient)
    # framing
    rank_id_framing = str(patient["record_id"]) + "_" + str(patient["trial_day_counter"]) + "_frame"
    patient["rank_id_framing_t0"] = rank_id_framing
    context = get_framing_context(patient)
    actions = get_framing_actions()

    frame_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_framing)
    response = client.rank(rank_request=frame_rank_request)
    framing_ranked = response.reward_action_id

    patient = update_framing_ranking(patient, framing_ranked)

    # history
    
    if patient["disconnectedness"] == 1 and patient["trial_day_counter"] > 7:
        rank_id_history = str(patient["record_id"]) + "_" + str(patient["trial_day_counter"]) + "_history"
        patient["rank_id_history_t0"] = rank_id_history
        context = get_history_context(patient)
        actions = get_history_actions()
        
        history_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_history)
        history_response = client.rank(rank_request=history_rank_request)
        history_ranked = history_response.reward_action_id

    else:
        rank_id_history = None
        patient["rank_id_history_t0"] = None
        history_ranked = "noHistory"
        
        
    patient = update_history_ranking(patient, history_ranked)

    # social
    rank_id_social = str(patient["record_id"]) + "_" + str(patient["trial_day_counter"]) + "_social"
    patient["rank_id_social_t0"] = rank_id_social
    context = get_social_context(patient)
    actions = get_social_actions()

    social_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_social)
    social_response = client.rank(rank_request=social_rank_request)
    social_ranked = social_response.reward_action_id

    patient = update_social_ranking(patient,social_ranked)

    # content
    rank_id_content = str(patient["record_id"]) + "_" + str(patient["trial_day_counter"]) + "_content"
    patient["rank_id_content_t0"] = rank_id_content
    context = get_content_context(patient)
    actions = get_content_actions()

    content_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_content)
    content_response = client.rank(rank_request=content_rank_request)
    content_ranked = content_response.reward_action_id

    patient = update_content_ranking(patient, content_ranked)

    # reflective
    rank_id_reflective = str(patient["record_id"]) + "_" + str(patient["trial_day_counter"]) + "_reflective"
    patient["rank_id_reflective_t0"] = rank_id_reflective
    context = get_reflective_context(patient)
    actions = get_reflective_actions()

    reflective_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_reflective)
    reflective_response = client.rank(rank_request=reflective_rank_request)
    reflective_ranked = reflective_response.reward_action_id

    patient = update_reflective_ranking(patient, reflective_ranked)
    
    patient = update_num_day_sms(patient)
    patient = updated_sms_today(patient)
    patient["trial_day_counter"] += 1
    return patient

def shift_t0_t1_rank_ids(patient):
    # shift these values for the next rank to store t0 values  
    patient["reward_value_t1"] = patient["reward_value_t0"]
    patient["flag_send_reward_value_t1"] = patient["flag_send_reward_value_t0"]
    patient["rank_id_framing_t1"] = patient["rank_id_framing_t0"]
    patient["rank_id_history_t1"] = patient["rank_id_history_t0"]
    patient["rank_id_social_t1"] = patient["rank_id_social_t0"]
    patient["rank_id_content_t1"] = patient["rank_id_content_t0"]
    patient["rank_id_reflective_t1"] = patient["rank_id_reflective_t0"]
    patient["reward_value_t0"] = 0
    patient["flag_send_reward_value_t0"] = False
    patient["rank_id_framing_t0"] = None
    patient["rank_id_history_t0"] = None
    patient["rank_id_social_t0"] = None
    patient["rank_id_content_t0"] = None
    patient["rank_id_reflective_t0"] = None
    return patient


def update_framing_ranking(patient, response_action_id_framing):
    patient["response_action_id_framing"] = response_action_id_framing
    if patient["response_action_id_framing"] == "posFrame":
        patient["framing_sms"] = 1
    elif patient["response_action_id_framing"] == "negFrame":
        patient["framing_sms"] = 2
    elif patient["response_action_id_framing"] == "neutFrame":
        patient["framing_sms"] = 0
    return patient

def update_history_ranking(patient, response_action_id_history):
    patient["response_action_id_history"] = response_action_id_history
    if patient["response_action_id_history"] == "yesHistory":
        patient["history_sms"] = 1
    elif patient["response_action_id_history"] == "noHistory":
        patient["history_sms"] = 0
    return patient

def update_social_ranking(patient, response_action_id_social):
    patient["response_action_id_social"] = response_action_id_social
    if patient["response_action_id_social"] == "yesSocial":
        patient["social_sms"] = 1
    elif patient["response_action_id_social"] == "noSocial":
        patient["social_sms"] = 0
    return patient

def update_content_ranking(patient, response_action_id_content):
    patient["response_action_id_content"] = response_action_id_content
    if patient["response_action_id_content"] == "yesContent":
        patient["content_sms"] = 1
    elif patient["response_action_id_content"] == "noContent":
        patient["content_sms"] = 0
    return patient

def update_reflective_ranking(patient, response_action_id_reflective):
    patient["response_action_id_reflective"] = response_action_id_reflective
    if patient["response_action_id_reflective"] == "yesReflective":
        patient["reflective_sms"] = 1
    elif patient["response_action_id_reflective"] == "noReflective":
        patient["reflective_sms"] = 0
    return patient

def update_num_day_sms(patient):
    if patient["response_action_id_framing"] == "posFrame":
        patient["num_day_since_pos_framing"] = 0
        patient["num_day_since_neg_framing"] += 1
        patient["num_day_since_no_sms"] = 0
    elif patient["response_action_id_framing"] == "negFrame":
        patient["num_day_since_neg_framing"] = 0
        patient["num_day_since_pos_framing"] += 1
        patient["num_day_since_no_sms"] = 0
    elif patient["response_action_id_framing"] == "neutFrame":
        patient["num_day_since_neg_framing"] += 1
        patient["num_day_since_pos_framing"] += 1

    if patient["response_action_id_history"] == "yesHistory":
        patient["num_day_since_history"] = 0
        patient["num_day_since_no_sms"] = 0
    elif patient["response_action_id_history"] == "noHistory":
        patient["num_day_since_history"] += 1

    if patient["response_action_id_social"] == "yesSocial":
        patient["num_day_since_social"] = 0
        patient["num_day_since_no_sms"] = 0
    elif patient["response_action_id_social"] == "noSocial":
        patient["num_day_since_social"] += 1

    if patient["response_action_id_content"] == "yesContent":
        patient["num_day_since_content"] = 0
        patient["num_day_since_no_sms"] = 0
    elif patient["response_action_id_content"] == "noContent":
        patient["num_day_since_content"] += 1

    if patient["response_action_id_reflective"] == "yesReflective":
        patient["num_day_since_reflective"] = 0
        patient["num_day_since_no_sms"] = 0
    elif patient["response_action_id_reflective"] == "noReflective":
        patient["num_day_since_reflective"] += 1

    if patient["response_action_id_framing"] == "neutFrame":
        if patient["response_action_id_history"] == "noHistory" and patient["response_action_id_social"] == "noSocial" and patient["response_action_id_content"] == "noContent" and patient["response_action_id_reflective"] == "noReflective":
            patient["num_day_since_no_sms"] += 1
    
    return patient

# Computes and updates the SMS text message to send to this patient today.
def updated_sms_today(patient):
    fp = build_path("_SMSChoices", "sms_choices.csv")
    sms_choices = pd.read_csv(fp)
    framing = patient["framing_sms"]
    history = patient["history_sms"]
    social = patient["social_sms"]
    content = patient["content_sms"]
    reflective = patient["reflective_sms"]
    print("records_id: ", patient["record_id"]," rankresult: ", framing, history, social, content, reflective)

    # TODO ask joe if this takes into account if the sms_choices 0,0,0,0,0 then will it return rows = None -> if so code is all set I modified, if not make sure it wont throw an error or fix the if else clause
    rows = sms_choices[sms_choices['framing_sms'] == framing]
    rows = rows[rows['history_sms'] == history]
    rows = rows[rows['social_sms'] == social]
    rows = rows[rows['content_sms'] == content]
    rows = rows[rows['reflective_sms'] == reflective]

  
    # If 0,0,0,0,0 is found, then the rows will be None, so our defaults are first, the empty text message
    text_number = 0
    factor_set = 0
    text = ""
    text_message = ""
    quantitative_sms = 0
    doctor_sms = 0
    lifestyle_sms = 0
    
    # If 0,0,0,0,0 is not found, then the rows will have some potential values,
    if not rows.empty:
        # Then we randomize what of the factor set text messages we will send
        row = rows.sample()
        # We record the factor_set and text_number as unique identifiers for this message
        factor_set = row['factor_set'].item()
        text_number = row['text_number'].item()
        quantitative_sms = row['quantitative_sms'].item()
        doctor_sms = row['doctor_sms'].item()
        lifestyle_sms = row['lifestyle_sms'].item()

        text_message = row['text_message'].item()
        # We store the text message that will be sent for this specific patient that takes into account the history of their adherence
        # This finds and replaces the "X" in the sms_choices text_message rows to customize to the patient.
        text = row['text_message'].item().replace("X", str(patient["total_dichot_adherence_past7"]))

    # We've updated the local variables and now store into the patient object as attributes to be exported in bulk by another function
    patient["text_number"] = text_number
    patient["factor_set"] = factor_set
    patient["text_message"] = text_message
    patient["quantitative_sms"] = quantitative_sms
    patient["doctor_sms"] = doctor_sms
    patient["lifestyle_sms"] = lifestyle_sms
    patient["sms_msg_today"] = text
    return patient

def get_demographics_features(patient):
    demographic_features = {"age": patient["age"],
                            "sex": patient["sex"],
                            "race_white": patient["race_white"],
                            "race_black": patient["race_black"],
                            "race_asian": patient["race_asian"],
                            "race_hispanic": patient["race_hispanic"],
                            "race_other": patient["race_other"],
                            "education_level": patient["edu_level"],
                            "employment_status": patient["employment_status"],
                            "marital_status": patient["marital_status"]}
    demographic_features_dict = {"demographic_features": demographic_features}
    return demographic_features_dict


def get_clinical_features(patient):
    clinical_features = {"num_physicians": patient["num_physicians"],
                         "num_years_dm_rx": patient["num_years_dm_rx"],
                         "hba1c": patient["hba1c"]}
    clinical_features_dict = {"clinical_features": clinical_features}
    return clinical_features_dict


def get_motivational_features(patient):
    motivational_features = {"automaticity": patient["automaticity"],
                             "pt_activation": patient["pt_activation"],
                             "reason_dm_rx": patient["reason_dm_rx"]}
    motivational_features_dict = {"motivational_features": motivational_features}
    return motivational_features_dict


def get_rx_use_features(patient):
    rx_use = {"num_rx": patient["num_rx"],
              "concomitant_insulin_use": patient["concomitant_insulin_use"],
              "non_adherence": patient["non_adherence"]}
    rx_use_dict = {"rx_use": rx_use}
    return rx_use_dict


def get_pillsy_med_features(patient):
    pillsy_med_features = {"num_twice_daily_pillsy_meds": patient["num_twice_daily_pillsy_meds"],
                           "pillsy_meds_agi": patient["pillsy_meds_agi"],
                           "pillsy_meds_dpp4": patient["pillsy_meds_dpp4"],
                           "pillsy_meds_glp1": patient["pillsy_meds_glp1"],
                           "pillsy_meds_meglitinide": patient["pillsy_meds_meglitinide"],
                           "pillsy_meds_metformin": patient["pillsy_meds_metformin"],
                           "pillsy_meds_sglt2": patient["pillsy_meds_sglt2"],
                           "pillsy_meds_sulfonylurea": patient["pillsy_meds_sulfonylurea"],
                           "pillsy_meds_thiazolidinedione": patient["pillsy_meds_thiazolidinedione"],
                           "num_pillsy_meds": patient["num_pillsy_meds_t0"]}
    pillsy_med_features_dict = {"pillsy_med_features": pillsy_med_features}
    return pillsy_med_features_dict


def get_observed_feedback_features(patient):
    observed_feedback_features = {}
    observed_feedback_features["disconnectedness"] = patient["disconnectedness"]
    if patient["early_rx_use"] != None:
        observed_feedback_features["early_rx_use"] = patient["early_rx_use"]
    if patient["avg_adherence_1day"] != None:
        observed_feedback_features["avg_adherence_1day"] = patient["avg_adherence_1day"]
        if patient["avg_adherence_3day"] != None:
            observed_feedback_features["avg_adherence_3day"] = patient["avg_adherence_3day"]
        if patient["avg_adherence_7day"] != None:
            observed_feedback_features["avg_adherence_7day"] = patient["avg_adherence_7day"]
        observed_feedback_features_dict = {"observed_feedback_features": observed_feedback_features}
    return observed_feedback_features_dict


def get_num_days_since_features(patient):
    num_days_since_features = {"num_day_since_no_sms": patient["num_day_since_no_sms"],
                               "num_day_since_pos_framing": patient["num_day_since_pos_framing"],
                               "num_day_since_neg_framing": patient["num_day_since_neg_framing"],
                               "num_day_since_history": patient["num_day_since_history"],
                               "num_day_since_social": patient["num_day_since_social"],
                               "num_day_since_content": patient["num_day_since_content"],
                               "num_day_since_reflective": patient["num_day_since_reflective"]}
    num_days_since_features_dict = {"num_days_since_features": num_days_since_features}
    return num_days_since_features_dict


def get_framing_context(patient):
    framing_context = [
        get_demographics_features(patient),
        get_clinical_features(patient),
        get_motivational_features(patient),
        get_rx_use_features(patient),
        get_pillsy_med_features(patient),
        get_observed_feedback_features(patient),
        get_num_days_since_features(patient)]
    return framing_context


def get_history_context(patient):
    history_context = [
        get_demographics_features(patient),
        get_clinical_features(patient),
        get_motivational_features(patient),
        get_rx_use_features(patient),
        get_pillsy_med_features(patient),
        get_observed_feedback_features(patient),
        get_num_days_since_features(patient),
        {"response_action_id_framing" : patient["response_action_id_framing"]}]
    return history_context


def get_social_context(patient):
    social_context = [
        get_demographics_features(patient),
        get_clinical_features(patient),
        get_motivational_features(patient),
        get_rx_use_features(patient),
        get_pillsy_med_features(patient),
        get_observed_feedback_features(patient),
        get_num_days_since_features(patient),
        {"response_action_id_framing" : patient["response_action_id_framing"]},
        {"response_action_id_history" : patient["response_action_id_history"]}]
    return social_context


def get_content_context(patient):
    content_context = [
        get_demographics_features(patient),
        get_clinical_features(patient),
        get_motivational_features(patient),
        get_rx_use_features(patient),
        get_pillsy_med_features(patient),
        get_observed_feedback_features(patient),
        get_num_days_since_features(patient),
        {"response_action_id_framing" : patient["response_action_id_framing"]},
        {"response_action_id_history" : patient["response_action_id_history"]},
        {"response_action_id_social" : patient["response_action_id_social"]}]
    return content_context


def get_reflective_context(patient):
    reflective_context = [
        get_demographics_features(patient),
        get_clinical_features(patient),
        get_motivational_features(patient),
        get_rx_use_features(patient),
        get_pillsy_med_features(patient),
        get_observed_feedback_features(patient),
        get_num_days_since_features(patient),
        {"response_action_id_framing" : patient["response_action_id_framing"]},
        {"response_action_id_history" : patient["response_action_id_history"]},
        {"response_action_id_social" : patient["response_action_id_social"]},
        {"response_action_id_content" : patient["response_action_id_content"]}]
    return reflective_context
