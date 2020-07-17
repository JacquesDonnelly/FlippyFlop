import datetime
import pickle
import random

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

# TODO: A single object API for cards and terms would be better


class RemainingCards:
    """Object for cards cookie"""
    def __init__(self, service=None, string=None):
        self.service = service
        self.cards = []
        self.delimiter = "-"
        self.service = service
        self.string = string

        if self.string:
            self.from_string(string)
        elif self.service:
            self.from_service()

    def from_string(self, string):
        self.cards = string.split(self.delimiter)

    def from_service(self):
        self.get_cards_from_service()
        self.shuffle_cards()

    def get_cards_from_service(self):
        self.cards = self.service.todays_cards()

    def shuffle_cards(self):
        random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop()

    def __str__(self):
        return self.delimiter.join(self.cards)

    def __len__(self):
        return len(self.cards)



TERMS = ff.get_terms()
