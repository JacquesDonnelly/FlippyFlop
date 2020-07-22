## Email
# "Ellie completed X out of Y cards so far today"
# Then a table with each row representing a bucket, columns of "Correct", "Incorrect"
# (later) add one or two incorrect cards for ad hoc tests

from typing import List
import pickle
import datetime
from googleapiclient.discovery import build
from app.flippyflop import FlippyFlop


credential_path = "app/auth/token.pickle"
with open(credential_path, "rb") as token:
    creds = pickle.load(token)

service = build("sheets", "v4", credentials=creds)
spreadsheet_id = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

ff = FlippyFlop(
    service=service,
    spreadsheet_id=spreadsheet_id,
    day_zero=datetime.datetime(2020, 7, 7),
    throttle_time=0,
)

# TODO: BNPR. Get a method in ff to get values from buckets rather than using "private"
values = ff._get_values(tab="buckets", cell_range="A:C")
bucket_df = pd.DataFrame(values[1:], columns=values[0])
bucket_df["date"] = pd.to_datetime(bucket_df["timestamp_tested"], unit="s").dt.date
today = pd.Timestamp("2020-07-15")
bucket_df_yest = bucket_df.query("date < @today")

def correct_on_date(bucket_df: pd.DataFrame, day: pd.Timestamp) -> dict:
    """give mapping of all cards to the results on that day

    the cards that are not tested should be mapped to None, whereas correct/incorrect
    cards should be mapped to True/False""" 
    

# TODO: BNPR. Think about a "Card" object that holds all historic bucktets. And 
# how would we use a collection of them to calculate the stats we want below?

def calculate_stats(cards_todo_on_date: List[int], result_on_date: dict) -> dict:
    """calculate statistics for given correct on date mapping

    Desired Stats:
        Total cards required
        Total card completed
        Buckets completed today (we can't do this with input above yet given
        we don't have the buckets of the cards in the args. What should we change?
        Maybe think about a "Card" object that holds all of the historic buckets. Then
        we can attach relevant computations to it)
        Percentage correct per bucket
        Percentage correct overall
    """

