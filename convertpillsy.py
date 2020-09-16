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


def import_pillsy(filepath):
    print("Importing Pillsy data")
    pillsy = pd.read_csv(filepath)
    pillsy.eventTime = pillsy.eventTime.astype(date)
    pillsy.YearDMRx = pillsy.YearDMRx.astype(int)
    return