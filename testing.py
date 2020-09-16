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


def importPillsy():
    date_cols = ["eventTime"]
    df = pd.read_csv("PillsyExample.csv", sep=',', parse_dates=date_cols)
    print("Printing dataframe")
    print(df)
    print("Printing dtypes")
    print(df.dtypes)
    print("Printing eventTime Column")
    print(df.eventTime)
    print("Printing eventTime Column Subtraction")
    print("Date 1: ", df.eventTime[10])
    print("Date 2: ", df.eventTime[0])
    print(df.eventTime[10] - df.eventTime[0])

#  set([<DiscreteFactor representing phi(x1:2, x2:3, x3:2) at 0x7f8e32b4ca10>,
#     <DiscreteFactor representing phi(x5:2, x7:2, x8:2) at 0x7f8e4c393690>,
#    <DiscreteFactor representing phi(x5:2, x6:2, x7:2) at 0x7f8e32b4c750>,
#   <DiscreteFactor representing phi(x3:2, x4:2, x1:2) at 0x7f8e32b4cb50>])

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    importPillsy()
