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
        """retreive what buckets we should do on a given timestamp"""
        buckets = []
        for period, box in self.day_gaps:
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
        self._bucket = None

    @property
    def current_bucket(self):
        if self._bucket:
            pass
        else:
            self._bucket = self._resolve_bucket()

        return self._bucket

    def _resolve_bucket(self):
        bucket = 1
        for result in self.results:
            if result:
                bucket = min(5, bucket + 1)
            else:
                bucket = max(1, bucket - 1) 
        return bucket


class Deck:
    """The entire collection of cards"""

    def __init__(self, cards: Sequence[Card], schedule: Schedule):
        self.cards = cards
        self.schedule = schedule

    def count_to_be_tested_today(self) -> int:
        todays_buckets = self.schedule.todays_buckets()
        todays_buckets = [int(bucket) for bucket in todays_buckets]
        cards_in_todays_bucket = [
            card for card in self.cards
            if card.current_bucket in todays_buckets
        ]
        import pdb; pdb.set_trace()
        # TODO: Currently we are freezing time but still have "future" results
        # in our card. So we should generalize Card._resolve_bucket to 
        # Card._resolve_bucket_on_date. Then we can test much better and 
        # widen scope for future stats
        return len(cards_in_todays_bucket)

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
        card_ids = df["card_id"].unique()
        cards = [cls._create_card_from_df(df, card_id) for card_id in card_ids]
        if schedule is None:
            schedule = Schedule()
        return cls(cards=cards, schedule=schedule)

    # TODO: BNPR: Technically now these static methods can be put somewhere else
    # But where? Maybe in card? Just module level funcitons?

    @staticmethod
    def _create_card_from_df(df, card_id):
        card_df = df.query("card_id == @card_id")
        results = Deck._extract_results(card_df)
        test_dates = Deck._extract_test_dates(card_df)
        return Card(_id=int(card_id), results=results, test_dates=test_dates)


    @staticmethod
    def _extract_results(card_df):
        bucket_sequence = card_df["bucket_after_test"].astype(int)
        bucket_sequence_shifted = bucket_sequence.shift(1).fillna(1)
        return (bucket_sequence > bucket_sequence_shifted).to_list()

    @staticmethod
    def _extract_test_dates(card_df):
        # TODO: BNPR: convert straight to datetme rather than Timstamp first
        test_dates = (
            pd.to_datetime(card_df["timestamp_tested"], unit="s")
            .to_list()
        )
        return [date.to_pydatetime() for date in test_dates]




def gather_deck_stats(deck: Deck) -> Dict[str, Real]:
    """ 
    Desired Stats:
        Total cards required
        Total card completed
        Buckets completed today 
        Percentage correct per bucket
        Percentage correct overall
    """
