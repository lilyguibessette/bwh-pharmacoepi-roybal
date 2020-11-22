<<<<<<< HEAD
import pandas as pd
import numpy as np
import math
import sys
import os
import re
import gc
import time
from datetime import datetime, date
from collections import Counter
import string
import pickle
import json
from data_classes import ContextFeatures

class Patient:
    def __init__(self, study_id,
                 start_date,
                 last_run_time,
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
                 race_native,
                 race_pacific,
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
                 #num_pillsy_meds,
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
        self.last_run_time = datetime.now()
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
        self.race_native = race_native
        self.race_pacific = race_pacific
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
        self.num_pillsy_meds = pillsy_meds_agi + pillsy_meds_dpp4 + pillsy_meds_glp1 + pillsy_meds_meglitinide + pillsy_meds_metformin + pillsy_meds_sglt2 + pillsy_meds_sulfonylurea + pillsy_meds_thiazolidinedione
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

    def shift_dichot_day_adherences(self, todays_avg_adherence):
        self.dichot_adherence_day7 = self.dichot_adherence_day6
        self.dichot_adherence_day6 = self.dichot_adherence_day5
        self.dichot_adherence_day5 = self.dichot_adherence_day4
        self.dichot_adherence_day4 = self.dichot_adherence_day3
        self.dichot_adherence_day3 = self.dichot_adherence_day2
        self.dichot_adherence_day2 = self.dichot_adherence_day1
        if todays_avg_adherence > 0:
            self.day1 = 1
        else:
            self.day1 = 0

    def shift_day_adherences(self, todays_avg_adherence):
        self.adherence_day7 = self.adherence_day6
        self.adherence_day6 = self.adherence_day5
        self.adherence_day5 = self.adherence_day4
        self.adherence_day4 = self.adherence_day3
        self.adherence_day3 = self.adherence_day2
        self.adherence_day2 = self.adherence_day1
        self.adherence_day1 = todays_avg_adherence

    def calc_avg_adherence(self):
        if self.trial_day_counter < 3:
            self.avg_adherence_7day = None
            self.avg_adherence_3day = None
            self.avg_adherence_1day = self.adherence_day1
        elif 3 <= self.daysFromStartCounter < 7:
            self.avg_adherence_7day = None
            self.avg_adherence_3day = (self.adherence_day1 + self.adherence_day2 + self.adherence_day3) / 3
            self.avg_adherence_1day = self.adherence_day1
        elif self.daysFromStartCounter >= 7:
            self.avg_adherence_7day = (self.adherence_day1 + self.adherence_day2 + self.adherence_day3 + self.adherence_day4 + self.adherence_day5 + self.adherence_day6 + self.adherence_day7) / 7
            self.avg_adherence_3day = (self.adherence_day1 + self.adherence_day2 + self.adherence_day3) / 3
            self.avg_adherence_1day = self.adherence_day1

    def update_framing_ranking(self, response_action_id_framing):
        self.response_action_id_framing = response_action_id_framing
        if self.response_action_id_framing == "posFrame":
            self.framing_sms = 1
        elif self.response_action_id_framing == "negFrame":
            self.framing_sms = 2
        elif self.response_action_id_framing == "neutFrame":
            self.framing_sms = 0

    def update_history_ranking(self, response_action_id_history):
        self.response_action_id_history = response_action_id_history
        if self.response_action_id_history == "yesHistory":
            self.history_sms = 1
        elif self.response_action_id_history == "noHistory":
            self.history_sms = 0

    def update_social_ranking(self, response_action_id_social):
        self.response_action_id_social = response_action_id_social
        if self.response_action_id_social == "yesSocial":
            self.social_sms = 1
        elif self.response_action_id_social == "noSocial":
            self.social_sms = 0

    def update_content_ranking(self, response_action_id_content):
        self.response_action_id_content = response_action_id_content
        if self.response_action_id_content == "yesContent":
            self.content_sms = 1
        elif self.response_action_id_content == "noContent":
            self.content_sms = 0


    def update_reflective_ranking(self, response_action_id_reflective):
        self.response_action_id_reflective = response_action_id_reflective
        if self.response_action_id_reflective == "yesReflective":
            self.reflective_sms = 1
        elif self.response_action_id_reflective == "noReflective":
            self.reflective_sms = 0


    def update_num_day_sms(self):
        if self.response_action_id_framing == "posFrame":
            self.num_day_since_pos_framing = 0
            self.num_day_since_neg_framing += 1
            self.num_day_since_no_sms = 0
        elif self.response_action_id_framing == "negFrame":
            self.num_day_since_neg_framing = 0
            self.num_day_since_pos_framing += 1
            self.num_day_since_no_sms = 0
        elif self.response_action_id_framing == "neutFrame":
            self.num_day_since_neg_framing += 1
            self.num_day_since_pos_framing += 1

        if self.response_action_id_history == "yesHistory":
            self.num_day_since_history = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_history == "noHistory":
            self.num_day_since_history += 1

        if self.response_action_id_social == "yesSocial":
            self.num_day_since_social = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_social == "noSocial":
            self.num_day_since_social += 1

        if self.response_action_id_content == "yesContent":
            self.num_day_since_content = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_content == "noContent":
            self.num_day_since_content += 1

        if self.response_action_id_reflective == "yesReflective":
            self.num_day_since_reflective = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_reflective == "noReflective":
            self.num_day_since_reflective += 1

        if self.response_action_id_framing == "neutFrame":
            if self.response_action_id_history == "noHistory" and self.response_action_id_social == "noSocial" and self.response_action_id_content == "noContent" and self.response_action_id_reflective == "noReflective":
                self.num_day_since_no_sms += 1

    def updated_sms_today(self, filepath):
        import os.path
        fp = os.path.join("..", "..", "..", "SMSChoices", "sms_choices.csv")
        sms_choices = pd.read_csv(fp)
        # filepath = "/Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/Protocol_Documents/sms_choices_vF_10-6-20.csv"
        # sms_choices = pd.read_csv(filepath)
        #TODO JOE
        # Joe you'll need these to compare to the sms_choices csv
        sms_coder = [self.framing_sms, self.history_sms, self.social_sms, self.content_sms, self.reflective_sms]
        # determind sms from csv
        text = "the sms from the csv"
        text.replace("X", self.total_dichot_adherence_past7)
        self.sms_today = text
        # and you'll need this for


    def get_framing_context(self):
        return json.dump(ContextFeatures.FramingContext(self))

    def update_redcap_pillsy_vars(self, num_twice_daily_pillsy_meds, pillsy_meds_agi, pillsy_meds_dpp4, pillsy_meds_glp1, pillsy_meds_meglitinide, pillsy_meds_metformin, pillsy_meds_sglt2, pillsy_meds_sulfonylurea, pillsy_meds_thiazolidinedione):
        self.num_twice_daily_pillsy_meds = num_twice_daily_pillsy_meds
        self.pillsy_meds_agi = pillsy_meds_agi
        self.pillsy_meds_dpp4 = pillsy_meds_dpp4
        self.pillsy_meds_glp1 = pillsy_meds_glp1
        self.pillsy_meds_meglitinide = pillsy_meds_meglitinide
        self.pillsy_meds_metformin = pillsy_meds_metformin
        self.pillsy_meds_sglt2 = pillsy_meds_sglt2
        self.pillsy_meds_sulfonylurea = pillsy_meds_sulfonylurea
        self.pillsy_meds_thiazolidinedione = pillsy_meds_thiazolidinedione
        self.num_pillsy_meds = pillsy_meds_agi + pillsy_meds_dpp4 + pillsy_meds_glp1 + pillsy_meds_meglitinide + pillsy_meds_metformin + pillsy_meds_sglt2 + pillsy_meds_sulfonylurea + pillsy_meds_thiazolidinedione

    def get_history_context(self):
        return ContextFeatures.HistoryContext(self)

    def get_social_context(self):
        return ContextFeatures.SocialContext(self)

    def get_content_context(self):
        return ContextFeatures.ContentContext(self)

    def get_reflective_context(self):
        return ContextFeatures.ReflectiveContext(self)

    # Convert to categorical variables function
    def convert_redcap_input_vars(self, ):

        # waiting for julie's response to email
=======
import pandas as pd
import numpy as np
import math
import sys
import os
import re
import gc
import time
from datetime import datetime, date
from collections import Counter
import string
import pickle
import json
from data_classes import ContextFeatures

class Patient:
    def __init__(self, study_id,
                 start_date,
                 last_run_time,
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
                 race_native,
                 race_pacific,
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
                 #num_pillsy_meds,
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
        self.last_run_time = datetime.now()
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
        self.race_native = race_native
        self.race_pacific = race_pacific
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
        #TODO question to julie about this waiting on response, might need to make sure no bugs come from junk string data or non-int data (want 1 or 0 for these variables)
        self.num_pillsy_meds = pillsy_meds_agi + pillsy_meds_dpp4 + pillsy_meds_glp1 + pillsy_meds_meglitinide + pillsy_meds_metformin + pillsy_meds_sglt2 + pillsy_meds_sulfonylurea + pillsy_meds_thiazolidinedione
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

    def shift_dichot_day_adherences(self, todays_avg_adherence):
        self.dichot_adherence_day7 = self.dichot_adherence_day6
        self.dichot_adherence_day6 = self.dichot_adherence_day5
        self.dichot_adherence_day5 = self.dichot_adherence_day4
        self.dichot_adherence_day4 = self.dichot_adherence_day3
        self.dichot_adherence_day3 = self.dichot_adherence_day2
        self.dichot_adherence_day2 = self.dichot_adherence_day1
        if todays_avg_adherence > 0:
            self.day1 = 1
        else:
            self.day1 = 0

    def shift_day_adherences(self, todays_avg_adherence):
        self.adherence_day7 = self.adherence_day6
        self.adherence_day6 = self.adherence_day5
        self.adherence_day5 = self.adherence_day4
        self.adherence_day4 = self.adherence_day3
        self.adherence_day3 = self.adherence_day2
        self.adherence_day2 = self.adherence_day1
        self.adherence_day1 = todays_avg_adherence

    def calc_avg_adherence(self):
        if self.trial_day_counter < 3:
            self.avg_adherence_7day = None
            self.avg_adherence_3day = None
            self.avg_adherence_1day = self.adherence_day1
        elif 3 <= self.daysFromStartCounter < 7:
            self.avg_adherence_7day = None
            self.avg_adherence_3day = (self.adherence_day1 + self.adherence_day2 + self.adherence_day3) / 3
            self.avg_adherence_1day = self.adherence_day1
        elif self.daysFromStartCounter >= 7:
            self.avg_adherence_7day = (self.adherence_day1 + self.adherence_day2 + self.adherence_day3 + self.adherence_day4 + self.adherence_day5 + self.adherence_day6 + self.adherence_day7) / 7
            self.avg_adherence_3day = (self.adherence_day1 + self.adherence_day2 + self.adherence_day3) / 3
            self.avg_adherence_1day = self.adherence_day1

    def update_framing_ranking(self, response_action_id_framing):
        self.response_action_id_framing = response_action_id_framing
        if self.response_action_id_framing == "posFrame":
            self.framing_sms = 1
        elif self.response_action_id_framing == "negFrame":
            self.framing_sms = 2
        elif self.response_action_id_framing == "neutFrame":
            self.framing_sms = 0

    def update_history_ranking(self, response_action_id_history):
        self.response_action_id_history = response_action_id_history
        if self.response_action_id_history == "yesHistory":
            self.history_sms = 1
        elif self.response_action_id_history == "noHistory":
            self.history_sms = 0

    def update_social_ranking(self, response_action_id_social):
        self.response_action_id_social = response_action_id_social
        if self.response_action_id_social == "yesSocial":
            self.social_sms = 1
        elif self.response_action_id_social == "noSocial":
            self.social_sms = 0

    def update_content_ranking(self, response_action_id_content):
        self.response_action_id_content = response_action_id_content
        if self.response_action_id_content == "yesContent":
            self.content_sms = 1
        elif self.response_action_id_content == "noContent":
            self.content_sms = 0

    def update_reflective_ranking(self, response_action_id_reflective):
        self.response_action_id_reflective = response_action_id_reflective
        if self.response_action_id_reflective == "yesReflective":
            self.reflective_sms = 1
        elif self.response_action_id_reflective == "noReflective":
            self.reflective_sms = 0

    def update_num_day_sms(self):
        if self.response_action_id_framing == "posFrame":
            self.num_day_since_pos_framing = 0
            self.num_day_since_neg_framing += 1
            self.num_day_since_no_sms = 0
        elif self.response_action_id_framing == "negFrame":
            self.num_day_since_neg_framing = 0
            self.num_day_since_pos_framing += 1
            self.num_day_since_no_sms = 0
        elif self.response_action_id_framing == "neutFrame":
            self.num_day_since_neg_framing += 1
            self.num_day_since_pos_framing += 1

        if self.response_action_id_history == "yesHistory":
            self.num_day_since_history = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_history == "noHistory":
            self.num_day_since_history += 1

        if self.response_action_id_social == "yesSocial":
            self.num_day_since_social = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_social == "noSocial":
            self.num_day_since_social += 1

        if self.response_action_id_content == "yesContent":
            self.num_day_since_content = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_content == "noContent":
            self.num_day_since_content += 1

        if self.response_action_id_reflective == "yesReflective":
            self.num_day_since_reflective = 0
            self.num_day_since_no_sms = 0
        elif self.response_action_id_reflective == "noReflective":
            self.num_day_since_reflective += 1

        if self.response_action_id_framing == "neutFrame":
            if self.response_action_id_history == "noHistory" and self.response_action_id_social == "noSocial" and self.response_action_id_content == "noContent" and self.response_action_id_reflective == "noReflective":
                self.num_day_since_no_sms += 1

    # Computes and updates the SMS text message to send to this patient today.
    def updated_sms_today(self):
        fp = os.path.join("..", "..", "SMSChoices", "sms_choices.csv")
        sms_choices = pd.read_csv(fp)
        #TODO ask joe if this takes into account if the sms_choices 0,0,0,0,0 then will it return rows = None -> if so code is all set I modified, if not make sure it wont throw an error or fix the if else clause
        rows = sms_choices.query(
            "framing_sms == @self.framing_sms "
            + "and history_sms == @self.history_sms "
            + "and social_sms == @self.social_sms "
            + "and content_sms == @self.content_sms"
            + "and reflective_sms == @self.reflective_sms"
        )
        #TODO Double check with Julie that randomization within the factor set of texts was the final decision (i.e. this is what we implemented)

        # If 0,0,0,0,0 is found, then the rows will be None, so our defaults are first, the empty text message
        text_number = 0
        factor_set = 0
        text = ""
        text_message = ""

        # If 0,0,0,0,0 is not found, then the rows will have some potential values,
        if rows != None:
            # Then we randomize what of the factor set text messages we will send
            row = rows.sample()
            # We record the factor_set and text_number as unique identifiers for this message
            factor_set = row['factor_set'].item()
            text_number = row['text_number'].item()
            text_message = row['text_message'].item()
            # We store the text message that will be sent for this specific patient that takes into account the history of their adherence
            # This finds and replaces the "X" in the sms_choices text_message rows to customize to the patient.
            text = row['text_message'].item().replace("X", str(self.total_dichot_adherence_past7))

        # We've updated the local variables and now store into the patient object as attributes to be exported in bulk by another function
        self.sms_today = text
        self.text_number = text_number
        self.factor_set = factor_set

    # Option for updates from REDCap data for changes in Pillsy medication use in follow up
    def update_redcap_pillsy_vars(self, num_twice_daily_pillsy_meds, pillsy_meds_agi, pillsy_meds_dpp4, pillsy_meds_glp1, pillsy_meds_meglitinide, pillsy_meds_metformin, pillsy_meds_sglt2, pillsy_meds_sulfonylurea, pillsy_meds_thiazolidinedione):
        self.num_twice_daily_pillsy_meds = num_twice_daily_pillsy_meds
        self.pillsy_meds_agi = pillsy_meds_agi
        self.pillsy_meds_dpp4 = pillsy_meds_dpp4
        self.pillsy_meds_glp1 = pillsy_meds_glp1
        self.pillsy_meds_meglitinide = pillsy_meds_meglitinide
        self.pillsy_meds_metformin = pillsy_meds_metformin
        self.pillsy_meds_sglt2 = pillsy_meds_sglt2
        self.pillsy_meds_sulfonylurea = pillsy_meds_sulfonylurea
        self.pillsy_meds_thiazolidinedione = pillsy_meds_thiazolidinedione
        self.num_pillsy_meds = pillsy_meds_agi + pillsy_meds_dpp4 + pillsy_meds_glp1 + pillsy_meds_meglitinide + pillsy_meds_metformin + pillsy_meds_sglt2 + pillsy_meds_sulfonylurea + pillsy_meds_thiazolidinedione


    def get_framing_context(self):
        #TODO might need to do {"contextFeatures": FramingContext()}
        return ContextFeatures.FramingContext(self)

    def get_history_context(self):
        return ContextFeatures.HistoryContext(self)

    def get_social_context(self):
        return ContextFeatures.SocialContext(self)

    def get_content_context(self):
        return ContextFeatures.ContentContext(self)

    def get_reflective_context(self):
        return ContextFeatures.ReflectiveContext(self)

    #TODO upon Julie Confirmation
    # Convert to categorical variables function
    def convert_redcap_input_vars(self):
        # confirm read in appropraitely or convert this to a date object : self.start_date
        if self.age == 1:
            self.age = "18-34"
        elif self.age == 2:
            self.age = "35-44"
        elif self.age == 3:
            self.age ="45-54"
        elif self.age == 4:
            self.age = "55-64"
        elif self.age == 5:
            self.age = "65-74"
        elif self.age == 6:
            self.age = "75-84"
        # self.age  # m
        # self.sex
        # self.num_years_dm_rx
        # self.hba1c
        # self.num_physicians = num_physicians
        # self.num_rx = num_rx
        # self.concomitant_insulin_use = concomitant_insulin_use
        # self.automaticity = automaticity
        # self.pt_activation = pt_activation
        # self.reason_dm_rx = reason_dm_rx
        # self.non_adherence = non_adherence
        # self.edu_level = edu_level
        # self.employment_status = employment_status
        # self.marital_status = marital_status
        # self.num_twice_daily_pillsy_meds = num_twice_daily_pillsy_meds
        # self.pillsy_meds_agi = pillsy_meds_agi
        # self.pillsy_meds_dpp4 = pillsy_meds_dpp4
        # self.pillsy_meds_glp1 = pillsy_meds_glp1
        # self.pillsy_meds_meglitinide = pillsy_meds_meglitinide
        # self.pillsy_meds_metformin = pillsy_meds_metformin
        # self.pillsy_meds_sglt2 = pillsy_meds_sglt2
        # self.pillsy_meds_sulfonylurea = pillsy_meds_sulfonylurea
        # self.pillsy_meds_thiazolidinedione = pillsy_meds_thiazolidinedione
        #
        #
        # row['start_date'],
        # row['age'],
        # row['sex'],
        # row['num_years_dm_rx'],
        # row['hba1c'],
        # row['race___1'],
        # row['race___2'],
        # row['race___3'],
        # row['race___4'],
        # row['race___5'],
        # row['race___6'],
        # row['race___7'],
        # row['num_physicians'],
        # row['num_rx'],
        # row['concomitant_insulin_use'],
        # row['automaticity'],
        # row['pt_activation'],
        # row['reason_dm_rx'],
        # row['non_adherence'],
        # row['edu_level'],
        # row['employment_status'],
        # row['marital_status'],
        # row['num_twice_daily_pillsy_meds'],
        # row['pillsy_meds___1'],
        # row['pillsy_meds___2'],
        # row['pillsy_meds___3'],
        # row['pillsy_meds___4'],
        # row['pillsy_meds___5'],
        # row['pillsy_meds___6'],
        # row['pillsy_meds___7'],
        # row['pillsy_meds___8'],
        # waiting for julie's response to email
>>>>>>> f4ea9f77adc91d9941245d47074699761fcafc1f
