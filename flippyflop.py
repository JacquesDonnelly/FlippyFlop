from throttle import throttle
import pandas as pd
import datetime
import time


# TODO: What happens if a card is deleted?
# TODO: Use type hinting
# TODO: Lint

class FlippyFlop:
    def __init__(self, service, spreadsheet_id):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        # TODO: get schedule from the schedule tab
        self.schedule = [(1, 1), (2, 2), (3, 3), (5, 4), (9, 5)]
        # TODO: start date should be a parameter
        # TODO: start date is actually day before start. fefactor to day 0
        self.start_date = datetime.datetime(2019, 12, 31)
        self.time_of_last_hit = time.time()

    def get_terms(self):
        """All terms in the terms tab"""
        values = self._get_values(tab="terms", cell_range="A:C")
        terms_df = pd.DataFrame(values[1:], columns=values[0])
        return terms_df.set_index("card_id")

    def get_buckets(self):
        """most recent bucket according to bucket tab"""
        values = self._get_values(tab="buckets", cell_range="A:C")
        bucket_df = pd.DataFrame(values[1:], columns=values[0])
        return (
            bucket_df.sort_values("timestamp_tested")
            .groupby("card_id")[["bucket_after_test", "timestamp_tested"]]
            .last()
        )

    def todays_cards(self):
        """get ids of cards left to do today"""
        terms = self.get_terms()
        buckets = self.get_buckets()
        terms = terms.join(buckets)
        today = self._todays_buckets()
        is_in_today = terms["bucket_after_test"].isin(today)
        earliest_today = datetime.datetime.utcnow().date().strftime("%s")
        not_seen_today = terms["timestamp_tested"] < earliest_today
        not_in_bucket_yet = terms["bucket_after_test"].isna()

        return terms[
            (is_in_today & not_seen_today) | not_in_bucket_yet
        ].index.tolist()

    @throttle
    def update_bucket(self, card_id, success):
        """add new row to buckets tab"""
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
    def add_term(self, front, back):
        largest_card = int(self.get_terms().index.max())
        # TODO: refactor repeated chunk of code below.
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

    def _todays_buckets(self):
        buckets = []
        for period, box in self.schedule:
            if (
                datetime.datetime.utcnow() - self.start_date
            ).days % period == 0:
                buckets.append(str(box))
        return buckets

    @throttle
    def _get_values(self, tab, cell_range):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(
                spreadsheetId=self.spreadsheet_id, range=f"{tab}!{cell_range}"
            )
            .execute()
        )
        return result["values"]

