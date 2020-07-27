from typing import Dict, Sequence, List
import datetime
from numbers import Real

import pandas as pd

from app.flippyflop import FlippyFlop


# TODO: BNPR move this to app.flippyflop and use it in FlippyFlop
class Schedule:
    """what buckets on what day"""

    def __init__(self):
        self.day_gaps = [(1, 1), (2, 2), (3, 3), (5, 4), (9, 5)]
        self.day_zero = datetime.datetime(2019, 12, 31)

    def buckets_for_timestamp(self, timestamp):
        """retreive waht buckets we should do on a given timestamp"""
        buckets = []
        for period, box in self.schedule:
            if (timestamp - self.day_zero).days % period == 0:
                buckets.append(str(box))
        return buckets

    def todays_buckets(self) -> List[str]:
        """retreive what buckets we should be reviewing today"""
        return self.buckets_for_timestamp(datetime.datetime.utcnow())


class Card:
    def __init__(
        self, _id: int, results: List[bool], test_dates: List[datetime.datetime]
    ):
        """
        results should have all test dates up to and including today
        True for correct, False for incorrect...
        """
        self.id = _id
        self.results = results
        self.test_dates = test_dates


class Deck:
    """The entire collection of cards"""

    def __init__(self, cards: Sequence[Card], schedule: Schedule):
        self.cards = cards
        self.schedule = schedule

    def count_to_be_tested_today(self) -> int:
        pass

    def count_completed_so_far_today(self) -> int:
        pass

    def percentage_correct_today(self) -> int:
        pass

    def total_correct_today(self) -> int:
        pass

    def total_incorrect_today(self) -> int:
        pass

    def card_by_id(self, _id) -> Card:
        for card in self.cards:
            if card.id == _id:
                return card

    @classmethod
    def from_df(cls, df, schedule=None):
        cards = []
        for card_id in df["card_id"].unique():
            card_df = df.query("card_id == @card_id")
            bucket_sequence = card_df["bucket_after_test"].astype(int)
            bucket_sequence_shifted = bucket_sequence.shift(1).fillna(1)
            results = (bucket_sequence > bucket_sequence_shifted).to_list()
            test_dates = (
                pd.to_datetime(card_df["timestamp_tested"], unit="s")
                .to_list()
            )
            test_dates = [date.to_pydatetime() for date in test_dates]
            cards.append(Card(_id=int(card_id), results=results, test_dates=test_dates))

        if schedule is None:
            schedule = Schedule()
        return cls(cards=cards, schedule=schedule)


def gather_deck_stats(deck: Deck) -> Dict[str, Real]:
    """ 
    Desired Stats:
        Total cards required
        Total card completed
        Buckets completed today 
        Percentage correct per bucket
        Percentage correct overall
    """