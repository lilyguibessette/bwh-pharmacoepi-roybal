# Used to represent the current patient data
#   - i.e. before update with Pillsy from yesterday / what would be used for tomorrow's run
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

def load_dict_pickle(pickle_file):
    with open(pickle_file, 'rb') as pfile:
        pickle_dict = pickle.load(pfile)
    return pickle_dict




