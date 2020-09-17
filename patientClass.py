import pandas as pd
import sys
import os
import re
import gc
import time
import datetime
from collections import Counter
import string
import pickle
import json


class Patient:
    def __init__(self, patientId, age, sex, yearDMRx, hba1c, clinicLocation, referralType, race, numMD, numRx, numDMRx,
                 insulinUse, pillboxUse, automaticity, ptActivation, reasonDMRx, nonAdhere, eduLevel, employed,
                 maritalStat, incomeLevel, num2XPillsy, numPillsyRx):
        self.patientId = patientId
        self.age = age
        self.sex = sex
        self.yearDMRx = yearDMRx
        self.hba1c = hba1c
        self.clinicLocation = clinicLocation
        self.referralType = referralType
        self.race = race
        self.numMD = numMD
        self.numRx = numRx
        self.numDMRx = numDMRx
        self.insulinUse = insulinUse
        self.pillboxUse = pillboxUse
        self.automaticity = automaticity
        self.ptActivation = ptActivation
        self.reasonDMRx = reasonDMRx
        self.nonAdhere = nonAdhere
        self.eduLevel = eduLevel
        self.employed = employed
        self.maritalStat = maritalStat
        self.incomeLevel = incomeLevel
        self.num2XPillsy = num2XPillsy
        self.numPillsyRx = numPillsyRx

    def update_avg_adherence(self, avgAdhere7, avgAdhere3, avgAdhere1):
        self.avgAdhere7 = avgAdhere7
        self.avgAdhere3 = avgAdhere3
        self.avgAdhere1 = avgAdhere1

    def update_days_since_SMS(self, numDaySincePosFraming, numDaySinceNegFraming, numDaySinceHistory, numDaySinceSocial,
                              numDaySinceContent, numDaySinceReflective):
        self.numDaySincePosFraming = numDaySincePosFraming
        self.numDaySinceNegFraming = numDaySinceNegFraming
        self.numDaySinceHistory = numDaySinceHistory
        self.numDaySinceSocial = numDaySinceSocial
        self.numDaySinceContent = numDaySinceContent
        self.numDaySinceReflective = numDaySinceReflective

    def update_ranking(self, framing, history, social, content, reflective):
        self.framing = framing
        self.history = history
        self.social = social
        self.content = content
        self.reflective = reflective

    def update_day_adherence(self, day7, day6, day5, day4, day3, day2, day1):
        self.day7 = day7
        self.day6 = day6
        self.day5 = day5
        self.day4 = day4
        self.day3 = day3
        self.day2 = day2
        self.day1 = day1


def import_demographics(filepath):
    print("Importing patient data")
    demographics = pd.read_csv(filepath)



def write_data(patient_records):
    new_file = str(datetime.now().strftime('%Y_%m_%d'))
    out_file = open(new_file, "w")
    out_file.write('variable headings')
    for patient in patient_records:
        # Step 2
        out_file.write(patient + '\n')
    out_file.close()


if __name__ == '__main__':
    # First time only
    demograph_file_path = input("Demographics File Path: ")
    patient_demographics = import_demographics(demograph_file_path)


    patient = Patient("patientId", 25, 0, 1995, 8.9, 3, 2, 3, 1, 2, 3, 0, 1, 0, 1, 1, 1, 1, 1, 2, 3, 1, 1)
    print(patient)
    pt_dict = vars(patient)
    print(pt_dict)
    patient.update_ranking(2,1,1,0,1)
    print(patient)
    pt_dict = vars(patient)
    print(pt_dict)
