from typing import Dict, Sequence
import datetime
from numbers import Real

from app.flippyflop import FlippyFlop

# TODO: Think about how to create the schedule class.
# I dont want to rely on the service.
# Maybe just replicate the code (ff._buckets_for_timestamp) 
# for now and revisit when creating DB?
class Schedule:
    """what buckets on what day"""

    def __init__(self, ff: FlippyFlop):
        self.ff = ff


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

    @classmethod
    def from_df(cls, df, schedule):
        cards = []
        for card_id in df["card_id"].unique():
            card_df = df.query("card_id == @card_id")
            bucket_sequence = card_df["bucket_after_test"].astype(int)
            bucket_sequence_shifted = bucket_sequence.shift(1).fillna(1)
            results = bucket_sequence > bucket_sequence_shifted
            # test_dates = ** convert int times to list of datetimes **
            cards.append(Card(_id=card_id, results=results, test_dates=test_dates))

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
