import pytest
from typing import List, Optional
import pickle
from googleapiclient.discovery import build

PROD_SPREADSHEET_ID = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

TEST_SPREADSHEET_ID = "1UDLGeqhVxfHJF5zk2EWRnWuQrZLQkCbwdg9loyd1nFg"


@pytest.fixture(scope="function")
def generate_dummy_service():
    def get_service(
        buckets_values: Optional[List] = None, terms_values: Optional[List] = None
    ):
        if not buckets_values:
            buckets_values = [
                ["card_id", "timestamp_tested", "bucket_after_test"],
                [1, 1577865600, 1],  # 2020-01-01 08:00:00
                [2, 1577865660, 2],  # 2020-01-01 08:01:00
            ]
        if not terms_values:
            terms_values = [
                ["card_id", "front", "back"],
                [1, "Capital of France?", "Paris"],
                [2, "Square root of four?", "Two"],
                [3, "How many legs does a horse have?", "Four"],
            ]

        service = build_service(credential_path="./app/auth/token.pickle")
        clear_entire_tab(service=service, tab="terms")
        clear_entire_tab(service=service, tab="buckets")
        write_values_to_tab(service=service, tab="terms", values=terms_values)
        write_values_to_tab(service=service, tab="buckets", values=buckets_values)

        return service

    return get_service


# TODO: BNPR what's the type of the service? add to typing everywhere
def build_service(credential_path: str):
    with open(credential_path, "rb") as token:
        creds = pickle.load(token)

    return build("sheets", "v4", credentials=creds)


def clear_entire_tab(service, tab: str) -> None:
    service.spreadsheets().values().clear(
        spreadsheetId=TEST_SPREADSHEET_ID, range=f"{tab}!A:Z"
    ).execute()


def write_values_to_tab(service, tab: str, values: List) -> None:
    body = {"values": values}
    service.spreadsheets().values().update(
        spreadsheetId=TEST_SPREADSHEET_ID,
        range=f"{tab}!A:C",
        body=body,
        valueInputOption="RAW",
    ).execute()
