# TODO:  add one or two incorrect cards for ad hoc tests

from typing import Sequence, List, Dict
from numbers import Real
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

