import json
# ***** Important issue to solve: JSON Dumps command to ignore attributes with None or Null or NaN values.
# ****** HOW TO FORMAT THE RESULTS FROM PREVIOUS CALL

# For each patient, and for each SMS category, each RankRequest will require a slightly modified ContextFeature
# Since each rank call takes into account the output decision of Personalizer at each stepwise RankRequest.
# i.e. the History RankRequest takes into account the result of the Framing RankRequest Result.
class FramingContext:
    def __init__(self, patient):
        self.demographics = json.dumps(Demographic(patient).__dict__)
        self.clinical = json.dumps(Clinical(patient).__dict__)
        self.motivational = json.dumps(Motivational(patient).__dict__)
        self.rxUse = json.dumps(RxUse(patient).__dict__)
        self.pillsy = json.dumps(PillsyMedications(patient).__dict__)
        self.observed_feedback = json.dumps(ObservedFeedback(patient).__dict__)
        self.num_days_since_sms = json.dumps(NumDaysSinceSMS(patient).__dict__)

class HistoryContext:
    def __init__(self, patient):
        self.demographics = json.dumps(Demographic(patient).__dict__)
        self.clinical = json.dumps(Clinical(patient).__dict__)
        self.motivational = json.dumps(Motivational(patient).__dict__)
        self.rxUse = json.dumps(RxUse(patient).__dict__)
        self.pillsy = json.dumps(PillsyMedications(patient).__dict__)
        self.observed_feedback = json.dumps(ObservedFeedback(patient).__dict__)
        self.num_days_since_sms = json.dumps(NumDaysSinceSMS(patient).__dict__)
        self.framing = patient.response_action_id_framing

class SocialContext:
    def __init__(self, patient):
        self.demographics = json.dumps(Demographic(patient).__dict__)
        self.clinical = json.dumps(Clinical(patient).__dict__)
        self.motivational = json.dumps(Motivational(patient).__dict__)
        self.rxUse = json.dumps(RxUse(patient).__dict__)
        self.pillsy = json.dumps(PillsyMedications(patient).__dict__)
        self.observed_feedback = json.dumps(ObservedFeedback(patient).__dict__)
        self.num_days_since_sms = json.dumps(NumDaysSinceSMS(patient).__dict__)
        self.framing = patient.response_action_id_framing
        self.history = patient.response_action_id_history

class ContentContext:
    def __init__(self, patient):
        self.demographics = json.dumps(Demographic(patient).__dict__)
        self.clinical = json.dumps(Clinical(patient).__dict__)
        self.motivational = json.dumps(Motivational(patient).__dict__)
        self.rxUse = json.dumps(RxUse(patient).__dict__)
        self.pillsy = json.dumps(PillsyMedications(patient).__dict__)
        self.observed_feedback = json.dumps(ObservedFeedback(patient).__dict__)
        self.num_days_since_sms = json.dumps(NumDaysSinceSMS(patient).__dict__)
        self.framing = patient.response_action_id_framing
        self.history = patient.response_action_id_history
        self.social = patient.response_action_id_social

class ReflectiveContext:
    def __init__(self, patient):
        self.demographics = json.dumps(Demographic(patient).__dict__)
        self.clinical = json.dumps(Clinical(patient).__dict__)
        self.motivational = json.dumps(Motivational(patient).__dict__)
        self.rxUse = json.dumps(RxUse(patient).__dict__)
        self.pillsy = json.dumps(PillsyMedications(patient).__dict__)
        self.observed_feedback = json.dumps(ObservedFeedback(patient).__dict__)
        self.num_days_since_sms = json.dumps(NumDaysSinceSMS(patient).__dict__)
        self.framing = patient.response_action_id_framing
        self.history = patient.response_action_id_history
        self.social = patient.response_action_id_social
        self.content = patient.response_action_id_content

# Namespaces stored within a Patient that will be standard & used in each of the above Context Features for each RankRequest
# The relevant patient object will be passed in to instantiate each of the namespaces.
class Demographic:
    def __init__(self, patient):
        self.age = patient.age
        self.sex = patient.sex
        self.race_white = patient.race_white
        self.race_black = patient.race_black
        self.race_asian = patient.race_asian
        self.race_hispanic = patient.race_hispanic
        self.race_other = patient.race_other
        self.edu_level = patient.edu_level
        self.employment_status = patient.employment_status
        self.marital_status = patient.marital_status

class Clinical:
    def __init__(self,  patient):
        self.num_physicians = patient.num_physicians
        self.num_years_dm_rx = patient.num_years_dm_rx
        self.hba1c = patient.hba1c

class Motivational:
    def __init__(self, patient):
        self.automaticity = patient.automaticity
        self.pt_activation = patient.pt_activation
        self.reason_dm_rx = patient.reason_dm_rx

class RxUse:
    def __init__(self, patient):
        self.num_rx = patient.num_rx
        self.concomitant_insulin_use = patient.concomitant_insulin_use
        self.non_adherence = patient.non_adherence

class PillsyMedications:
    def __init__(self, patient):
        self.num_twice_daily_pillsy_meds = patient.num_twice_daily_pillsy_meds
        self.pillsy_meds_agi = patient.pillsy_meds_agi
        self.pillsy_meds_dpp4 = patient.pillsy_meds_dpp4
        self.pillsy_meds_glp1 = patient.pillsy_meds_glp1
        self.pillsy_meds_meglitinide = patient.pillsy_meds_meglitinide
        self.pillsy_meds_metformin = patient.pillsy_meds_metformin
        self.pillsy_meds_sglt2 = patient.pillsy_meds_sglt2
        self.pillsy_meds_sulfonylurea = patient.pillsy_meds_sulfonylurea
        self.pillsy_meds_thiazolidinedione = patient.pillsy_meds_thiazolidinedione
        self.num_pillsy_meds = patient.num_pillsy_meds

class ObservedFeedback:
    def __init__(self, patient):
        if patient.avg_adherence_7day != None:
            self.avg_adherence_7day = patient.avg_adherence_7day
        if patient.avg_adherence_3day != None:
            self.avg_adherence_3day = patient.avg_adherence_3day
        if patient.avg_adherence_1day != None:
            self.avg_adherence_1day = patient.avg_adherence_1day
        if patient.early_rx_use_before_sms != None:
            self.early_rx_use_before_sms = patient.early_rx_use_before_sms

class NumDaysSinceSMS:
    def __init__(self, patient):
        self.num_day_since_no_sms = patient.num_day_since_no_sms
        self.num_day_since_pos_framing = patient.num_day_since_pos_framing
        self.num_day_since_neg_framing = patient.num_day_since_neg_framing
        self.num_day_since_history = patient.num_day_since_history
        self.num_day_since_social = patient.num_day_since_social
        self.num_day_since_content = patient.num_day_since_content
        self.num_day_since_reflective = patient.num_day_since_reflective
