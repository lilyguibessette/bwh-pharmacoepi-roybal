# <Dependencies>
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials

# Framing Actions
def get_framing_actions():
    posFrame = RankableAction(id='posFrame', features=[{"frame": "positive"}])
    negFrame = RankableAction(id='negFrame', features=[{"frame": "negative"}])
    neutFrame = RankableAction(id='neutFrame', features=[{"frame": "neutral"}])
    return [posFrame, negFrame, neutFrame]

# History Actions
def get_history_actions():
    yesHistory = RankableAction(id='yesHistory', features=[{"history": 1}])
    noHistory = RankableAction(id='noHistory', features=[{"history": 0}])
    return [yesHistory, noHistory]

# Social Actions
def get_social_actions():
    yesSocial = RankableAction(id='yesSocial', features=[{"social": 1}])
    noSocial = RankableAction(id='noSocial', features=[{"social": 0}])
    return [yesSocial, noSocial]


# Content Actions
def get_content_actions():
    yesContent = RankableAction(id='yesContent', features=[{"content": 1}])
    noContent = RankableAction(id='noContent', features=[{"content": 0}])
    return [yesContent, noContent]


# Reflective Actions
def get_reflective_actions():
    yesReflective = RankableAction(id='yesReflective', features=[{"reflective": 1}])
    noReflective = RankableAction(id='noReflective', features=[{"reflective": 0}])
    return [yesReflective, noReflective]


