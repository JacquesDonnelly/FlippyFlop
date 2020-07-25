"""Card selection logic and read/write to google sheets"""

from typing import List
import datetime
import time

import pandas as pd

# TODO: What happens if a card is deleted?


class FlippyFlop:
    def __init__(
        self,
        service,
        spreadsheet_id,
        throttle_time=1,
        day_zero=datetime.datetime(2019, 12, 31),
    ):
        """Handle reading and writing to google sheets and daily card logic"""
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        # TODO: get schedule from the schedule tab
        self.schedule = [(1, 1), (2, 2), (3, 3), (5, 4), (9, 5)]
        self.day_zero = day_zero
        self.time_of_last_hit = time.time()
        self.throttle_time = throttle_time

    def throttle(func):
        """ensure api requests are at least `throttle_time` apart"""

        # TODO: Should this be defined outside of class? E0213 & E1102 from pylint
        def inner(self, *args, **kwargs):
            time_since = time.time() - self.time_of_last_hit
            if abs(time_since) > self.throttle_time:
                _result = func(self, *args, **kwargs)
                self.time_of_last_hit = time.time()
                print(
                    f"hitting sheets via {func.__name__} with args {args} and kwargs {kwargs}"
                )
            else:
                time.sleep(0.1)
                _result = inner(self, *args, **kwargs)

            return _result

        return inner

    def get_terms(self) -> pd.DataFrame:
        """All terms in the terms tab"""
        values = self._get_values(tab="terms", cell_range="A:C")
        terms_df = pd.DataFrame(values[1:], columns=values[0])
        return terms_df.set_index("card_id")

    # TODO BNPR: refactor to get_current_buckets
    def get_buckets(self) -> pd.DataFrame:
        """Current bucket of each term"""
        bucket_df = self.get_all_buckets()
        return (
            bucket_df.sort_values("timestamp_tested")
            .groupby("card_id")[["bucket_after_test", "timestamp_tested"]]
            .last()
        )

    def get_all_buckets(self) -> pd.DataFrame:
        """Get everything from the buckets tab"""
        values = self._get_values(tab="buckets", cell_range="A:C")
        bucket_df = pd.DataFrame(values[1:], columns=values[0])
        return bucket_df

    def todays_cards(self) -> List[str]:
        """get ids of cards left to do today"""
        terms = self.get_terms()
        buckets = self.get_buckets()
        terms = terms.join(buckets)
        today = self._todays_buckets()
        is_in_today = terms["bucket_after_test"].isin(today)
        earliest_today = datetime.datetime.utcnow().date().strftime("%s")
        not_seen_today = terms["timestamp_tested"] < earliest_today
        not_in_bucket_yet = terms["bucket_after_test"].isna()

        return terms[(is_in_today & not_seen_today) | not_in_bucket_yet].index.tolist()

    @throttle
    def update_bucket(self, card_id: str, success: bool) -> None:
        """add new row to buckets tab indicating completion of card"""
        old_buckets = self.get_buckets()
        if card_id in old_buckets.index:
            old_bucket = int(old_buckets.loc[card_id]["bucket_after_test"])
        else:
            old_bucket = 1
        if success:
            change = 1
        else:
            change = -1
        new_bucket = min(max(1, old_bucket + change), 5)

        value_range_body = {
            "values": [[int(card_id)], [int(time.time())], [new_bucket]],
            "majorDimension": "COLUMNS",
        }

        (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range="buckets!A:C",
                valueInputOption="RAW",
                body=value_range_body,
            )
            .execute()
        )

    @throttle
    def add_term(self, front: str, back: str) -> None:
        """add new flash card to terms tab of google sheets

        by default the id column is just incremented by 1
        """
        largest_card = int(self.get_terms().index.max())
        # TODO: refactor repeated chunk of code.
        # A single execute method to avoid need for throttle decorator
        value_range_body = {
            "values": [[largest_card + 1], [front], [back]],
            "majorDimension": "COLUMNS",
        }

        (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range="terms!A1:D3",
                valueInputOption="RAW",
                body=value_range_body,
            )
            .execute()
        )

    def _todays_buckets(self) -> List[str]:
        """retreive what buckets we should be reviewing today"""
        return self._buckets_for_timestamp(datetime.datetime.utcnow())


    def _buckets_for_timestamp(self, timestamp):
        buckets = []
        for period, box in self.schedule:
            if (timestamp - self.day_zero).days % period == 0:
                buckets.append(str(box))
        return buckets


    @throttle
    def _get_values(self, tab: str, cell_range: str) -> List[List[str]]:
        """generic read cell range from google sheet tab"""
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=f"{tab}!{cell_range}")
            .execute()
        )
        return result["values"]
