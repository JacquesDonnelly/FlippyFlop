from typing import Dict, Sequence
import datetime
from numbers import Real


class Card:
    def __init__(
        self,
        _id: int,
        results: Dict[datetime.datetime, bool],
    ):
        """
        results should have all test dates up to and including today
        True for correct, False for incorrect...
        """
        self.id = _id
        self.results = results


class Deck:
    """The entire collection of cards"""
    def __init__(self, cards: Sequence[Card]):
        self.cards = cards

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
    def from_df(cls):
        pass
    

def gather_deck_stats(deck: Deck) -> Dict[str, Real]:
    """ 
    Desired Stats:
        Total cards required
        Total card completed
        Buckets completed today 
        Percentage correct per bucket
        Percentage correct overall
    """
