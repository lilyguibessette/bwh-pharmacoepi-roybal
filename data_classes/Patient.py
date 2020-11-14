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

    def update_days_since_SMS(self, num_day_since_pos_framing,
                              num_day_since_neg_framing,
                              num_day_since_history,
                              num_day_since_social,
                              num_day_since_content,
                              num_day_since_reflective):
        self.num_day_since_pos_framing = num_day_since_pos_framing
        self.num_day_since_neg_framing = num_day_since_neg_framing
        self.num_day_since_history = num_day_since_history
        self.num_day_since_social = num_day_since_social
        self.num_day_since_content = num_day_since_content
        self.num_day_since_reflective = num_day_since_reflective

    # fix depending on how rank outputs
    def update_framing_ranking(self, response_action_id_framing):
        self.response_action_id_framing = response_action_id_framing

    def update_history_ranking(self, response_action_id_history):
        self.response_action_id_history = response_action_id_history

    def update_social_ranking(self, response_action_id_social):
        self.response_action_id_social = response_action_id_social

    def update_content_ranking(self, response_action_id_content):
        self.response_action_id_content = response_action_id_content

    def update_reflective_ranking(self, response_action_id_reflective):
        self.response_action_id_reflective = response_action_id_reflective
