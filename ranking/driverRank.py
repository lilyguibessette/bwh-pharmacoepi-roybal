# <Dependencies>
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankRequest
from msrest.authentication import CognitiveServicesCredentials
from data_classes.Actions import get_framing_actions
from data_classes.Actions import get_history_actions
from data_classes.Actions import get_social_actions
from data_classes.Actions import get_content_actions
from data_classes.Actions import get_reflective_actions
from data_classes.Patient import Patient
import data_classes.ContextFeatures
from datetime import datetime, date, timedelta
import pytz
import os
import pandas as pd


def write_sms_history(pt_dict, run_time):
    sms_hist_filename = str(run_time.date()) + "_sms_history" + '.csv'
    sms_hist_filepath = os.path.join("..", "..", "..", "SMSHistory", sms_hist_filename)

    # Subset updated_pt_dict to what we need for reward calls and put in dataframe
    # create an Empty DataFrame object
    column_values = ['study_id', 'factor_set', 'text_number', 'sms_today', 'possibly_disconnected', 'trial_day_counter']
    sms_history_dataframe = pd.DataFrame(columns=column_values)

    for pt, data in pt_dict:
        # Reward value, Rank_Id's
        new_row = [data.study_id, data.factor_set, data.text_number,
                   data.sms_today, data.possibly_disconnected, data.trial_day_counter]
        sms_history_dataframe.loc[len(sms_history_dataframe)] = new_row
    # Writes CSV for RA to send text messages.
    sms_history_dataframe.to_csv(sms_hist_filepath)
    return


def run_ranking(patient, client, run_time):

# framing
    rank_id_framing = str(patient.get_study_id() + "_" + patient.counter() + "_frame")
    context = patient.get_framing_context()
    actions = get_framing_actions()

    frame_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_framing)
    response = client.rank(rank_request=frame_rank_request)
    framing_ranked = response.rewardActionId

    patient.update_framing_ranking(framing_ranked)

# history
    rank_id_history = str(patient.get_study_id() + "_" + patient.counter() + "_history")
    context = patient.get_history_context()
    actions = get_history_actions()

    history_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_history)
    history_response = client.rank(rank_request=history_rank_request)
    history_ranked = history_response.rewardActionId

    patient.update_history_ranking(history_ranked)

# social
    rank_id_social = str(patient.get_study_id() + "_" + patient.counter() + "_social")
    context = patient.get_context()
    actions = get_social_actions()

    social_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_social)
    social_response = client.rank(rank_request=social_rank_request)
    social_ranked = social_response.rewardActionId

    patient.update_social_ranking(social_ranked)

# content
    rank_id_content = str(patient.get_study_id() + "_" + patient.counter() + "_content")
    context = patient.get_context()
    actions = get_content_actions()

    content_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_content)
    content_response = client.rank(rank_request=content_rank_request)
    content_ranked = content_response.rewardActionId

    patient.update_content_ranking(content_ranked)

# reflective
    rank_id_reflective = str(patient.get_study_id() + "_" + patient.counter() + "_reflective")
    context = patient.get_context()
    actions = get_reflective_actions()

    reflective_rank_request = RankRequest(actions=actions, context_features=context, event_id=rank_id_reflective)
    reflective_response = client.rank(rank_request=reflective_rank_request)
    reflective_ranked = reflective_response.rewardActionId

    patient.update_reflective_ranking(reflective_ranked)

    patient.update_num_day_sms()
    patient.updated_sms_today()
    patient.last_run_time = pytz.UTC.localize(run_time)
    patient.counter += 1

    return patient

