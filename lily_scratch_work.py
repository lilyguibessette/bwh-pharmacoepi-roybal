from datetime import datetime, date, timedelta
import pandas as pd
import pytz

def import_Pillsy():
    import pandas as pd
    fp = "/Users/lilybessette/Dropbox (Partners HealthCare)/SHARED -- REINFORCEMENT LEARNING/Pillsy/2020-11-18_pillsy.csv"
    date_cols = ["eventTime"]
    pillsy = pd.read_csv(fp, sep=',', parse_dates=date_cols)
    pillsy.drop("patientId", axis=1, inplace=True)
    pillsy.drop("lastname", axis=1, inplace=True)
    pillsy.drop("method", axis=1, inplace=True)
    pillsy.drop("platform", axis=1, inplace=True)
    return pillsy




from datetime import datetime, date, timedelta
pillsy = import_Pillsy()
yesterday = pytz.UTC.localize(datetime(2020,11,17,10,30))
today = date(2020,11,18)
midnight = pytz.UTC.localize(datetime.combine(today, datetime.min.time()))

pillsy_subset = pillsy[pillsy["firstname"] == 15].copy()
pillsy_yesterday_subset = pillsy_subset[pillsy_subset["eventTime"] < midnight].copy()
pillsy_yesterday_subset = pillsy_yesterday_subset[pillsy_yesterday_subset["eventTime"] >= yesterday].copy()
pillsy_today_subset = pillsy_subset[midnight <= pillsy_subset["eventTime"]].copy()


for index, row in drug_subset.iterrows():
    if row['eventValue'] == "OPEN":
        first_time = row['eventTime']
        print(first_time)


def get_drugName_list(patient_entries):
    drugNames_df = patient_entries['drugName']
    unique_drugNames_df = drugNames_df.drop_duplicates()
    unique_drugNames_df_list = unique_drugNames_df.values.tolist()
    return unique_drugNames_df_list


