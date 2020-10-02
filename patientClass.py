import pandas as pd
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


class Patient:
    def __init__(self, study_id, startDate, age, sex, yearDMRx, hba1c, race, numMD, numRx, insulinUse, automaticity,
                 ptActivation, reasonDMRx, nonAdhere, eduLevel, employed, maritalStat, num2XPillsy, use_agi, use_dpp4,
                 use_glp1, use_meglitinide, use_metformin, use_sglt2, use_sulfonylurea, use_thiazolidinedione,
                 numPillsyRx):
        self.study_id = study_id
        self.startDate = datetime.date(datetime.strptime(startDate, '%m/%d/%y'))
        self.counter = datetime.date(datetime.now()) - self.startDate
        self.demographics = Demographic(age, sex, race, eduLevel, employed, maritalStat)
        self.clinical = Clinical(yearDMRx, hba1c, numMD)
        self.motivational = Motivational(automaticity, ptActivation, reasonDMRx)
        self.rxUse = RxUse(insulinUse, nonAdhere, numRx)
        self.pillsy = Pillsy(num2XPillsy, use_agi, use_dpp4, use_glp1, use_meglitinide, use_metformin, use_sglt2,
                             use_sulfonylurea, use_thiazolidinedione, numPillsyRx)
        self.list_pillsy_history = []

    def calc_avg_adherence(self):
        if self.counter < 3:
            self.avgAdhere7 = None  # ask if 0 or none should be used here
            self.avgAdhere3 = None  # ask if 0 or none should be used here
            self.avgAdhere1 = self.day1
        elif 3 <= self.counter < 7:
            self.avgAdhere7 = None  # ask if 0 or none should be used here
            self.avgAdhere3 = (self.day1 + self.day2 + self.day3) / 3
            self.avgAdhere1 = self.day1
        elif self.counter >= 7:
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

    def update_day_adherence(self, day7, day6, day5, day4, day3, day2, day1):
        self.day7 = day7
        self.day6 = day6
        self.day5 = day5
        self.day4 = day4
        self.day3 = day3
        self.day2 = day2
        self.day1 = day1

    def get_counter(self):
        return self.counter

    def get_study_id(self):
        return self.study_id

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


class Demographic:
    def __init__(self, age, sex, race, eduLevel, employed, maritalStat):
        self.age = age
        self.sex = sex
        self.race = race
        self.eduLevel = eduLevel
        self.employed = employed
        self.maritalStat = maritalStat

    def toJSON(self):
        json = json.dumps(self.__dict__)
        # json = " { demographics: " + json +


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


class Pillsy:
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
    def __init__(self, avgAdhere7, avgAdhere3, avgAdhere1):
        self.avgAdhere7 = avgAdhere7
        self.avgAdhere3 = avgAdhere3
        self.avgAdhere1 = avgAdhere1


def import_redcap(filepath):
    print("Importing patient data")
    redcap = pd.read_csv(filepath)
    return redcap


def write_data(patient_records):
    new_file = str(datetime.now().strftime('%Y_%m_%d'))
    out_file = open(new_file, "w")
    out_file.write('variable headings')
    for patient in patient_records:
        # Step 2
        out_file.write(patient + '\n')
    out_file.close()


def import_patient_data(filepath):
    pt_dict = load_dict_pickle(feature_dict_file)
    return pt_dict


if __name__ == '__main__':
    demograph_file_path = input("Demographics File Path: ")
    # /Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/data/RedCapExample.csv
    patient_demographics = import_redcap(demograph_file_path)
    demograph_file_path = input("Patient Data File Path: ")
    print(patient_demographics)



    for pt in patient_demographics:
        patient = Patient(pt.study_id, pt.startDate, pt.age, pt.sex, pt.yearDMRx, pt.hba1c, pt.race,
                                       pt.numMD, pt.numRx, pt.insulinUse, pt.automaticity, pt.ptActivation,
                                       pt.reasonDMRx, pt.nonAdhere, pt.eduLevel, pt.employed, pt.maritalStat,
                                       pt.num2XPillsy, pt.use_agi, pt.use_dpp4, pt.use_glp1, pt.use_meglitinide,
                                       pt.use_metformin, pt.use_sglt2, pt.use_sulfonylurea, pt.use_thiazolidinedione,
                                       pt.numPillsyRx)
        if pt.study_id not in pt_dict.keys():
            pt_dict[pt.study_id] = patient
        elif pt.study_id in pt_dict.keys():
            old_patient = pt_dict[pt.study_id]
            pt_dict[pt.study_id] = patient
            patient.update_days_since_SMS(old_patient.numDaySincePosFraming, old_patient.numDaySinceNegFraming, old_patient.numDaySinceHistory, old_patient.numDaySinceSocial,old_patient.numDaySinceContent, old_patient.numDaySinceReflective)
            patient.update_day_adherence(old_patient.day7, old_patient.day6, old_patient.day5, old_patient.day4, old_patient.day3, old_patient.day2, old_patient.day1)

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
