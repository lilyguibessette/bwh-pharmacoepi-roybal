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


class Patient:
    def __init__(self, study_id, start_date, age, sex, yearDMRx, hba1c, race_white, race_black, race_asian,
                 race_hispanic, race_other, numMD, numRx, insulinUse, automaticity,
                 ptActivation, reasonDMRx, nonadhere, edulevel, employed, maritalstat, num2xpillsy, use_agi, use_dpp4,
                 use_glp1, use_meglitinide, use_metformin, use_sglt2, use_sulfonylurea, use_thiazolidinedione,
                 numPillsyRx):
        self.studyID = str(study_id)
        self.startDate = datetime.date(datetime.strptime(start_date, '%m/%d/%y'))
        self.daysFromStartCounter = math.floor(datetime.date(datetime.now()) - self.startDate)
        self.demographics = Demographic(age, sex, race_white, race_black, race_asian, race_hispanic, race_other,
                                        edulevel, employed, maritalstat)
        self.clinical = Clinical(yearDMRx, hba1c, numMD)
        self.motivational = Motivational(automaticity, ptActivation, reasonDMRx)
        self.rxUse = RxUse(insulinuse, nonadhere, numrx)
        self.pillsy = Pillsy(num2xpillsy, use_agi, use_dpp4, use_glp1, use_meglitinide, use_metformin, use_sglt2,
                             use_sulfonylurea, use_thiazolidinedione, numPillsyRx)
        self.numDaySincePosFraming = 0
        self.numDaySinceNegFraming = 0
        self.numDaySinceHistory = 0
        self.numDaySinceSocial = 0
        self.numDaySinceContent = 0
        self.numDaySinceReflective = 0

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



#TO DO
#need to ensure that they can update numtwicedailyrxs and numpillsymeds