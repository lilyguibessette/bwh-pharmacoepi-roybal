import pandas as pd
import numpy as np
import math
import sys
import os
import re
import gc
import time
from datetime import datetime
from collections import Counter
import string
import pickle
import json


class RLDataPoint:
    def __init__(self, study_id,
                 start_date,
                 current_date,
                 trial_day_counter,
                 censor,
                 age,
                 sex,
                 num_years_dm_rx,
                 hba1c,
                 race_white,
                 race_black,
                 race_asian,
                 race_hispanic,
                 race_other,
                 num_physicians,
                 num_rx,
                 concomitant_insulin_use,
                 automaticity,
                 pt_activation,
                 reason_dm_rx,
                 non_adherence,
                 edu_level,
                 employment_status,
                 marital_status,
                 num_twice_daily_pillsy_meds,
                 pillsy_meds_agi,
                 pillsy_meds_dpp4,
                 pillsy_meds_glp1,
                 pillsy_meds_meglitinide,
                 pillsy_meds_metformin,
                 pillsy_meds_sglt2,
                 pillsy_meds_sulfonylurea,
                 pillsy_meds_thiazolidinedione,
                 num_pillsy_meds,
                 avg_adherence_7day,
                 avg_adherence_3day,
                 avg_adherence_1day,
                 adherence_day1,
                 adherence_day2,
                 adherence_day3,
                 adherence_day4,
                 adherence_day5,
                 adherence_day6,
                 adherence_day7,
                 dichot_adherence_day1,
                 dichot_adherence_day2,
                 dichot_adherence_day3,
                 dichot_adherence_day4,
                 dichot_adherence_day5,
                 dichot_adherence_day6,
                 dichot_adherence_day7,
                 total_dichot_adherence_past7,
                 early_rx_use_before_sms,
                 possibly_disconnected_day1,
                 possibly_disconnected_day2,
                 possibly_disconnected,
                 possibly_disconnected_date,
                 dates_possibly_disconnected,
                 num_dates_possibly_disconnected,
                 num_possibly_disconnected_indicator_true,
                 num_day_since_no_sms,
                 num_day_since_pos_framing,
                 num_day_since_neg_framing,
                 num_day_since_history,
                 num_day_since_social,
                 num_day_since_content,
                 num_day_since_reflective,
                 sms_msg_today,
                 factor_set,
                 text_number,
                 text_message,
                 framing_sms,
                 history_sms,
                 social_sms,
                 content_sms,
                 reflective_sms,
                 quantitative_sms,
                 doctor_sms,
                 lifestyle_sms,
                 response_action_id_framing,
                 response_action_id_history,
                 response_action_id_social,
                 response_action_id_content,
                 response_action_id_reflective,
                 rank_id_framing,
                 rank_id_history,
                 rank_id_social,
                 rank_id_content,
                 rank_id_reflective,
                 reward_value):
        self.study_id = str(study_id)
        self.start_date = start_date
        self.current_date = current_date
        self.trial_day_counter = trial_day_counter
        self.censor = censor
        self.age = age
        self.sex = sex
        self.num_years_dm_rx = num_years_dm_rx
        self.hba1c = hba1c
        self.race_white = race_white
        self.race_black = race_black
        self.race_asian = race_asian
        self.race_hispanic = race_hispanic
        self.race_other = race_other
        self.num_physicians = num_physicians
        self.num_rx = num_rx
        self.concomitant_insulin_use = concomitant_insulin_use
        self.automaticity = automaticity
        self.pt_activation = pt_activation
        self.reason_dm_rx = reason_dm_rx
        self.non_adherence = non_adherence
        self.edu_level = edu_level
        self.employment_status = employment_status
        self.marital_status = marital_status
        self.num_twice_daily_pillsy_meds = num_twice_daily_pillsy_meds
        self.pillsy_meds_agi = pillsy_meds_agi
        self.pillsy_meds_dpp4 = pillsy_meds_dpp4
        self.pillsy_meds_glp1 = pillsy_meds_glp1
        self.pillsy_meds_meglitinide = pillsy_meds_meglitinide
        self.pillsy_meds_metformin = pillsy_meds_metformin
        self.pillsy_meds_sglt2 = pillsy_meds_sglt2
        self.pillsy_meds_sulfonylurea = pillsy_meds_sulfonylurea
        self.pillsy_meds_thiazolidinedione = pillsy_meds_thiazolidinedione
        self.num_pillsy_meds = num_pillsy_meds
        self.avg_adherence_7day = avg_adherence_7day
        self.avg_adherence_3day = avg_adherence_3day
        self.avg_adherence_1day = avg_adherence_1day
        self.adherence_day1 = adherence_day1
        self.adherence_day2 = adherence_day2
        self.adherence_day3 = adherence_day3
        self.adherence_day4 = adherence_day4
        self.adherence_day5 = adherence_day5
        self.adherence_day6 = adherence_day6
        self.adherence_day7 = adherence_day7
        self.dichot_adherence_day1 = dichot_adherence_day1
        self.dichot_adherence_day2 = dichot_adherence_day2
        self.dichot_adherence_day3 = dichot_adherence_day3
        self.dichot_adherence_day4 = dichot_adherence_day4
        self.dichot_adherence_day5 = dichot_adherence_day5
        self.dichot_adherence_day6 = dichot_adherence_day6
        self.dichot_adherence_day7 = dichot_adherence_day7
        self.total_dichot_adherence_past7 = total_dichot_adherence_past7
        self.early_rx_use_before_sms = early_rx_use_before_sms
        self.possibly_disconnected_day1 = possibly_disconnected_day1
        self.possibly_disconnected_day2 = possibly_disconnected_day2
        self.possibly_disconnected = possibly_disconnected
        self.possibly_disconnected_date = possibly_disconnected_date
        self.dates_possibly_disconnected = dates_possibly_disconnected
        self.num_dates_possibly_disconnected = num_dates_possibly_disconnected
        self.num_possibly_disconnected_indicator_true = num_possibly_disconnected_indicator_true
        self.num_day_since_no_sms = num_day_since_no_sms
        self.num_day_since_pos_framing = num_day_since_pos_framing
        self.num_day_since_neg_framing = num_day_since_neg_framing
        self.num_day_since_history = num_day_since_history
        self.num_day_since_social = num_day_since_social
        self.num_day_since_content = num_day_since_content
        self.num_day_since_reflective = num_day_since_reflective
        self.sms_msg_today = sms_msg_today
        self.factor_set = factor_set
        self.text_number = text_number
        self.text_message = text_message
        self.framing_sms = framing_sms
        self.history_sms = history_sms
        self.social_sms = social_sms
        self.content_sms = content_sms
        self.reflective_sms = reflective_sms
        self.quantitative_sms = quantitative_sms
        self.doctor_sms = doctor_sms
        self.lifestyle_sms = lifestyle_sms
        self.response_action_id_framing = response_action_id_framing
        self.response_action_id_history = response_action_id_history
        self.response_action_id_social = response_action_id_social
        self.response_action_id_content = response_action_id_content
        self.response_action_id_reflective = response_action_id_reflective
        self.rank_id_framing = rank_id_framing
        self.rank_id_history = rank_id_history
        self.rank_id_social = rank_id_social
        self.rank_id_content = rank_id_content
        self.rank_id_reflective = rank_id_reflective
        self.reward_value = reward_value

    class PtContextFeatDataPoint:
        def __init__(self, study_id,
                     start_date,
                     current_date,
                     trial_day_counter,
                     age,
                     sex,
                     num_years_dm_rx,
                     hba1c,
                     race_white,
                     race_black,
                     race_asian,
                     race_hispanic,
                     race_other,
                     num_physicians,
                     num_rx,
                     concomitant_insulin_use,
                     automaticity,
                     pt_activation,
                     reason_dm_rx,
                     non_adherence,
                     edu_level,
                     employment_status,
                     marital_status,
                     num_twice_daily_pillsy_meds,
                     pillsy_meds_agi,
                     pillsy_meds_dpp4,
                     pillsy_meds_glp1,
                     pillsy_meds_meglitinide,
                     pillsy_meds_metformin,
                     pillsy_meds_sglt2,
                     pillsy_meds_sulfonylurea,
                     pillsy_meds_thiazolidinedione,
                     num_pillsy_meds,
                     avg_adherence_7day,
                     avg_adherence_3day,
                     avg_adherence_1day,
                     early_rx_use_before_sms,
                     num_day_since_no_sms,
                     num_day_since_pos_framing,
                     num_day_since_neg_framing,
                     num_day_since_history,
                     num_day_since_social,
                     num_day_since_content,
                     num_day_since_reflective,
                     rank_id_framing,
                     rank_id_history,
                     rank_id_social,
                     rank_id_content,
                     rank_id_reflective):
            self.study_id = str(study_id)
            self.start_date = start_date
            self.current_date = current_date
            self.trial_day_counter = trial_day_counter
            self.age = age
            self.sex = sex
            self.num_years_dm_rx = num_years_dm_rx
            self.hba1c = hba1c
            self.race_white = race_white
            self.race_black = race_black
            self.race_asian = race_asian
            self.race_hispanic = race_hispanic
            self.race_other = race_other
            self.num_physicians = num_physicians
            self.num_rx = num_rx
            self.concomitant_insulin_use = concomitant_insulin_use
            self.automaticity = automaticity
            self.pt_activation = pt_activation
            self.reason_dm_rx = reason_dm_rx
            self.non_adherence = non_adherence
            self.edu_level = edu_level
            self.employment_status = employment_status
            self.marital_status = marital_status
            self.num_twice_daily_pillsy_meds = num_twice_daily_pillsy_meds
            self.pillsy_meds_agi = pillsy_meds_agi
            self.pillsy_meds_dpp4 = pillsy_meds_dpp4
            self.pillsy_meds_glp1 = pillsy_meds_glp1
            self.pillsy_meds_meglitinide = pillsy_meds_meglitinide
            self.pillsy_meds_metformin = pillsy_meds_metformin
            self.pillsy_meds_sglt2 = pillsy_meds_sglt2
            self.pillsy_meds_sulfonylurea = pillsy_meds_sulfonylurea
            self.pillsy_meds_thiazolidinedione = pillsy_meds_thiazolidinedione
            self.num_pillsy_meds = num_pillsy_meds
            self.avg_adherence_7day = avg_adherence_7day
            self.avg_adherence_3day = avg_adherence_3day
            self.avg_adherence_1day = avg_adherence_1day
            self.early_rx_use_before_sms = early_rx_use_before_sms
            self.num_day_since_no_sms = num_day_since_no_sms
            self.num_day_since_pos_framing = num_day_since_pos_framing
            self.num_day_since_neg_framing = num_day_since_neg_framing
            self.num_day_since_history = num_day_since_history
            self.num_day_since_social = num_day_since_social
            self.num_day_since_content = num_day_since_content
            self.num_day_since_reflective = num_day_since_reflective
            self.rank_id_framing = rank_id_framing
            self.rank_id_history = rank_id_history
            self.rank_id_social = rank_id_social
            self.rank_id_content = rank_id_content
            self.rank_id_reflective = rank_id_reflective





    def calc_avg_adherence(self):
        if self.daysFromStartCounter < 3:
            self.avgAdhere7 = None
            self.avgAdhere3 = None
            self.avgAdhere1 = self.day1
        elif 3 <= self.daysFromStartCounter < 7:
            self.avgAdhere7 = None
            self.avgAdhere3 = (self.day1 + self.day2 + self.day3) / 3
            self.avgAdhere1 = self.day1
        elif self.daysFromStartCounter >= 7:
            self.avgAdhere7 = (self.day1 + self.day2 + self.day3 + self.day4 + self.day5 + self.day6 + self.day7) / 7
            self.avgAdhere3 = (self.day1 + self.day2 + self.day3) / 3
            self.avgAdhere1 = self.day1
        self.observedFeedback = ObservedFeedback(self.avgAdhere7, self.avgAdhere3, self.avgAdhere1)

    def update_days_since_SMS(self, numDaySincePosFraming, numDaySinceNegFraming, numDaySinceHistory, numDaySinceSocial,
                              numDaySinceContent, numDaySinceReflective):
        self.numDaySincePosFraming = numDaySincePosFraming
        self.numDaySinceNegFraming = numDaySinceNegFraming
        self.numDaySinceHistory = numDaySinceHistory
        self.numDaySinceSocial = numDaySinceSocial
        self.numDaySinceContent = numDaySinceContent
        self.numDaySinceReflective = numDaySinceReflective

    # fix depending on how rank outputs
    def update_framing_ranking(self, framing):
        self.framing = framing

    def update_history_ranking(self, history):
        self.history = history

    def update_social_ranking(self, social):
        self.social = social

    def update_content_ranking(self, content):
        self.content = content

    def update_reflective_ranking(self, reflective):
        self.reflective = reflective

    def update_day_adherence(self, day1, day2, day3, day4, day5, day6, day7):
        self.day7 = day7
        self.day6 = day6
        self.day5 = day5
        self.day4 = day4
        self.day3 = day3
        self.day2 = day2
        self.day1 = day1

    def get_daysFromStartCounter(self):
        return self.daysFromStartCounter

    def get_study_id(self):
        return self.study_id

    def get_demographics(self):
        return self.demographics

    def get_clinical(self):
        return self.clinical

    def get_motivational(self):
        return self.motivational

    def get_rxUse(self):
        return self.rxUse

    def get_pillsy(self):
        return self.pillsy

    def get_context(self):
        context = Context(self.demographics, self.clinical, self.motivational, self.rxUse, self.pillsy)
        context_features = "{ \"contextFeatures\": [" + " { demographics: " + context.demographics + "}, { clinical: " + context.clinical + "}, { motivational: " + context.motivational + "}, { rxUse: " + context.rxUse + "}, { pillsy: " + context.pillsy + "} } ] }"
        return context_features


class Context:
    def __init__(self, demographics, clinical, motivational, rxUse, pillsy):
        self.demographics = json.dumps(demographics.__dict__)
        self.clinical = json.dumps(clinical.__dict__)
        self.motivational = json.dumps(motivational.__dict__)
        self.rxUse = json.dumps(rxUse.__dict__)
        self.pillsy = json.dumps(pillsy.__dict__)


# <Namespaces stored within a Patient>
class Demographic:
    def __init__(self, age, sex, race_white, race_black, race_asian, race_hispanic, race_other, eduLevel, employed,
                 maritalStat):
        self.age = age
        self.sex = sex
        self.race_white = race_white
        self.race_black = race_black
        self.race_asian = race_asian
        self.race_hispanic = race_hispanic
        self.race_other = race_other
        self.eduLevel = eduLevel
        self.employed = employed
        self.maritalStat = maritalStat


class Clinical:
    def __init__(self, yearDMRx, hba1c, numMD):
        self.yearDMRx = yearDMRx
        self.hba1c = hba1c
        self.numMD = numMD


class Motivational:
    def __init__(self, automaticity, ptActivation, reasonDMRx):
        self.automaticity = automaticity
        self.ptActivation = ptActivation
        self.reasonDMRx = reasonDMRx


class RxUse:
    def __init__(self, insulinUse, nonAdhere, numRx):
        self.insulinUse = insulinUse
        self.numRx = numRx
        self.nonAdhere = nonAdhere


class PillsyMedications:
    def __init__(self, num2XPillsy, use_agi, use_dpp4, use_glp1, use_meglitinide, use_metformin, use_sglt2,
                 use_sulfonylurea, use_thiazolidinedione, numPillsyRx):
        self.num2XPillsy = num2XPillsy
        self.use_agi = use_agi
        self.use_dpp4 = use_dpp4
        self.use_glp1 = use_glp1
        self.use_meglitinide = use_meglitinide
        self.use_metformin = use_metformin
        self.use_sglt2 = use_sglt2
        self.use_sulfonylurea = use_sulfonylurea
        self.use_thiazolidinedione = use_thiazolidinedione
        self.numPillsyRx = numPillsyRx


class ObservedFeedback:
    def __init__(self, avgAdhere7, avgAdhere3, avgAdhere1, ):
        self.avgAdhere7 = avgAdhere7
        self.avgAdhere3 = avgAdhere3
        self.avgAdhere1 = avgAdhere1


def import_redcap(filepath):
    print("Importing patient RedCap data")
    redcap = pd.read_csv(filepath)
    return redcap


def write_data(patient_records):
    new_file = str(datetime.now().strftime('%Y_%m_%d'))
    new_file = "PatientTrialData_" + new_file
    out_file = open(new_file, "w")
    out_file.write('variable headings')
    for patient in patient_records:
        out_file.write(patient + '\n')
    out_file.close()


def load_dict_pickle(pic_file):
    with open(pic_file, 'rb') as pfile:
        feature_dict = pickle.load(pfile)
    return feature_dict


def import_patient_data_pickle(pt_dict_file_path):
    print("Importing patient trial pickle data")
    pt_dict = load_dict_pickle(pt_dict_file_path)
    return pt_dict


# import csv
# toCSV = [{'name':'bob','age':25,'weight':200},
#         {'name':'jim','age':31,'weight':180}]
# keys = toCSV[0].keys()
# with open('people.csv', 'w', newline='')  as output_file:
#    dict_writer = csv.DictWriter(output_file, keys)
#    dict_writer.writeheader()
#    dict_writer.writerows(toCSV)


if __name__ == '__main__':
    demograph_file_path = input("RedCap File Path: ")
    # /Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/data/RedCapExample.csv
    patient_demographics = import_redcap(demograph_file_path)
    print(patient_demographics)

    # pt_dict_file_path = input("Patient Data File Path: ")
    # pt_dict = import_patient_data_pickle(pt_dict_file_path)

    print(patient_demographics)

# patient = Patient("patientId", "9/1/20", 25, 0, 1995, 8.9, 3, 2, 3, 1,0,1,1, 2, 3, 0, 1, 0, 1, 1, 1, 1, 1, 2, 3, 1, 1)
#  print(patient)
# pt_dict = vars(patient)
# print(pt_dict)
#   #patient.update_ranking(2, 1, 1, 0, 1)
# print(patient)
# pt_dict = vars(patient)
# print(pt_dict)
# ptStr = patient.get_context()
# print(ptStr)


# TO DO
# need to ensure that they can update numtwicedailyrxs and numpillsymeds
