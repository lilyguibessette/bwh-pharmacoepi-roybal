# import json
# # ***** Important issue to solve: JSON Dumps command to ignore attributes with None or Null or NaN values.
# # ****** HOW TO FORMAT THE RESULTS FROM PREVIOUS CALL
#
# # For each patient, and for each SMS category, each RankRequest will require a slightly modified ContextFeature
# # Since each rank call takes into account the output decision of Personalizer at each stepwise RankRequest.
# # i.e. the History RankRequest takes into account the result of the Framing RankRequest Result.
# class FramingContext:
#     def __init__(self, patient):
#         self.demographics = json.dumps({"demographic":Demographic(patient)})
#         self.clinical = json.dumps({"clinical":Clinical(patient)})
#         self.motivational = json.dumps({"motivational":Motivational(patient)})
#         self.rxUse = json.dumps({"rxUse":RxUse(patient)})
#         self.pillsy = json.dumps({"pillsy_rxs",PillsyMedications(patient)})
#         self.observed_feedback = json.dumps({"observed_feedback": ObservedFeedback(patient)})
#         self.num_days_since_sms = json.dumps({"sms_history": NumDaysSinceSMS(patient)})
#     def get_context_features(self):
#         return [self.demographics, self.clinical, self.motivational, self.rxUse,
#                                  self.pillsy, self.observed_feedback, self.num_days_since_sms]
#
# class HistoryContext:
#     def __init__(self, patient):
#         self.demographics = json.dumps({"demographic":Demographic(patient)})
#         self.clinical = json.dumps({"clinical":Clinical(patient)})
#         self.motivational = json.dumps({"motivational":Motivational(patient)})
#         self.rxUse = json.dumps({"rxUse":RxUse(patient)})
#         self.pillsy = json.dumps({"pillsy_rxs",PillsyMedications(patient)})
#         self.observed_feedback = json.dumps({"observed_feedback": ObservedFeedback(patient)})
#         self.num_days_since_sms = json.dumps({"sms_history": NumDaysSinceSMS(patient)})
#         self.framing = patient.response_action_id_framing
#     def get_context_features(self):
#         return [self.demographics, self.clinical, self.motivational, self.rxUse, self.pillsy,
#                                  self.observed_feedback, self.num_days_since_sms, self.framing]
#
# class SocialContext:
#     def __init__(self, patient):
#         self.demographics = json.dumps({"demographic":Demographic(patient)})
#         self.clinical = json.dumps({"clinical":Clinical(patient)})
#         self.motivational = json.dumps({"motivational":Motivational(patient)})
#         self.rxUse = json.dumps({"rxUse":RxUse(patient)})
#         self.pillsy = json.dumps({"pillsy_rxs",PillsyMedications(patient)})
#         self.observed_feedback = json.dumps({"observed_feedback": ObservedFeedback(patient)})
#         self.num_days_since_sms = json.dumps({"sms_history": NumDaysSinceSMS(patient)})
#         self.framing = patient.response_action_id_framing
#         self.history = patient.response_action_id_history
#     def get_context_features(self):
#         return [self.demographics, self.clinical, self.motivational, self.rxUse, self.pillsy,
#                                  self.observed_feedback, self.num_days_since_sms, self.framing, self.history]
#
#
# class ContentContext:
#     def __init__(self, patient):
#         self.demographics = json.dumps({"demographic":Demographic(patient)})
#         self.clinical = json.dumps({"clinical":Clinical(patient)})
#         self.motivational = json.dumps({"motivational":Motivational(patient)})
#         self.rxUse = json.dumps({"rxUse":RxUse(patient)})
#         self.pillsy = json.dumps({"pillsy_rxs",PillsyMedications(patient)})
#         self.observed_feedback = json.dumps({"observed_feedback": ObservedFeedback(patient)})
#         self.num_days_since_sms = json.dumps({"sms_history": NumDaysSinceSMS(patient)})
#         self.framing = patient.response_action_id_framing
#         self.history = patient.response_action_id_history
#         self.social = patient.response_action_id_social
#
#     def get_context_features(self):
#         return  [self.demographics, self.clinical, self.motivational, self.rxUse, self.pillsy,
#                                  self.observed_feedback, self.num_days_since_sms, self.framing, self.history,
#                                  self.social]
#
# class ReflectiveContext:
#     def __init__(self, patient):
#         self.demographics = json.dumps({"demographic":Demographic(patient)})
#         self.clinical = json.dumps({"clinical":Clinical(patient)})
#         self.motivational = json.dumps({"motivational":Motivational(patient)})
#         self.rxUse = json.dumps({"rxUse":RxUse(patient)})
#         self.pillsy = json.dumps({"pillsy_rxs",PillsyMedications(patient)})
#         self.observed_feedback = json.dumps({"observed_feedback": ObservedFeedback(patient)})
#         self.num_days_since_sms = json.dumps({"sms_history": NumDaysSinceSMS(patient)})
#         self.framing = patient.response_action_id_framing
#         self.history = patient.response_action_id_history
#         self.social = patient.response_action_id_social
#         self.content = patient.response_action_id_content
#     def get_context_features(self):
#         return  [self.demographics, self.clinical, self.motivational, self.rxUse, self.pillsy,
#                                  self.observed_feedback, self.num_days_since_sms, self.framing, self.history,
#                                  self.social, self.content]
#
# # Namespaces stored within a Patient that will be standard & used in each of the above Context Features for each RankRequest
# # The relevant patient object will be passed in to instantiate each of the namespaces.

#
# class RxUse:
#     def __init__(self, patient):
#
#
# class PillsyMedications:
#     def __init__(self, patient):
#
#
# class ObservedFeedback:

#
# class NumDaysSinceSMS:
#     def __init__(self, patient):

