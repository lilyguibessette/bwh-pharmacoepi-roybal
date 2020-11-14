# <Dependencies>
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials
import datetime, json, os, time, uuid
from datetime import datetime
from actions import get_framing_actions
from actions import get_history_actions
from actions import get_social_actions
from actions import get_content_actions
from actions import get_reflective_actions
import patientClass

def getClient():
  # <AuthorizationVariables>
    personalizer_key = input("ENTER PERSONALIZER KEY: \n")
    personalizer_endpoint = input("ENTER PERSONALIZER ENDPOINT: \n")
    # <Client>
    # Instantiate a Personalizer client
    client = PersonalizerClient(personalizer_endpoint, CognitiveServicesCredentials(personalizer_key))
    return client

def runRanking(patient):

# framing
    frame_eventid = str(patient.get_study_id() + "_" + patient.counter() + "_frame")
    context = patient.get_context()
    actions = get_framing_actions()

    frame_rank_request = RankRequest(actions=actions, context_features=context, event_id=frame_eventid)
    response = client.rank(rank_request=frame_rank_request)
    framing_ranked = response.rewardActionId

    patient.update_framing_ranking(framing_ranked)

# history
    history_eventid = str(patient.get_study_id() + "_" + patient.counter() + "_history")
    context = patient.get_context()
    actions = get_history_actions()

    history_rank_request = RankRequest(actions=actions, context_features=context, event_id=history_eventid)
    history_response = client.rank(rank_request=history_rank_request)
    history_ranked = history_response.rewardActionId

    patient.update_history_ranking(history_ranked)

# social
    social_eventid = str(patient.get_study_id() + "_" + patient.counter() + "_social")
    context = patient.get_context()
    actions = get_social_actions()

    social_rank_request = RankRequest(actions=actions, context_features=context, event_id=social_eventid)
    social_response = client.rank(rank_request=social_rank_request)
    social_ranked = social_response.rewardActionId

    patient.update_social_ranking(social_ranked)

# content
    content_eventid = str(patient.get_study_id() + "_" + patient.counter() + "_content")
    context = patient.get_context()
    actions = get_content_actions()

    content_rank_request = RankRequest(actions=actions, context_features=context, event_id=content_eventid)
    content_response = client.rank(rank_request=content_rank_request)
    content_ranked = content_response.rewardActionId

    patient.update_content_ranking(content_ranked)

# reflective
    reflective_eventid = str(patient.get_study_id() + "_" + patient.counter() + "_reflective")
    context = patient.get_context()
    actions = get_reflective_actions()

    reflective_rank_request = RankRequest(actions=actions, context_features=context, event_id=reflective_eventid)
    reflective_response = client.rank(rank_request=reflective_rank_request)
    reflective_ranked = reflective_response.rewardActionId

    patient.update_reflective_ranking(reflective_ranked)

# write coder for updating the days since sms here


if __name__ == '__main__':

    client = getClient()




