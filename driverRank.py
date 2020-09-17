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

def getClient():
  # <AuthorizationVariables>
    personalizer_key = input("ENTER PERSONALIZER KEY: \n")
    personalizer_endpoint = input("ENTER PERSONALIZER ENDPOINT: \n")
    # <Client>
    # Instantiate a Personalizer client
    client = PersonalizerClient(personalizer_endpoint, CognitiveServicesCredentials(personalizer_key))
    return client

def runRanking(patient):
    eventid = str(patient.getPatientId() + datetime.now().strftime('%Y%m%d_%H%M%S'))
    context = patient.getContext()
    actions = get_framing_actions()
    # <rank>
    rank_request = RankRequest(actions=actions, context_features=context, excluded_actions=['juice'], event_id=eventid)
    response = client.rank(rank_request=rank_request)

    response.reward_action_id

if __name__ == '__main__':
    client = getClient()




