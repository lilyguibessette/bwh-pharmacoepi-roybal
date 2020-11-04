# <Dependencies>
import pandas as pd
import time
import datetime
from datetime import datetime
import pickle
import json
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials
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
from patientClass import import_redcap, import_patient_data_pickle

# </Dependencies>

if __name__ == '__main__':
    start = input("Trial Initiation? Y/N: ")
    demograph_file_path = input("RedCap File Path: ")
    # /Users/lilybessette/BWH_DoPE/bwh-pharmacoepi-roybal/data/RedCapExample.csv
    patient_demographics = import_redcap(demograph_file_path)
    pt_dict = {}
    if start == "N":
        pt_dict_file_path = input("Patient Data File Path: ")
        pt_dict = import_patient_data_pickle(pt_dict_file_path)




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



    replace("X", )