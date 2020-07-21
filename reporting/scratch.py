## Email
# "Ellie completed X out of Y cards so far today"
# Then a table with each row representing a bucket, columns of "Correct", "Incorrect"
# (later) add one or two incorrect cards for ad hoc tests

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

buckets = ff.get_buckets()
