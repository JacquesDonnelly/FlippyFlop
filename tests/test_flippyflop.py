from .functional_test_data import buckets, tests, terms_to_add
from freezegun import freeze_time
from googleapiclient.discovery import build
import flippyflop
import datetime
import os
import pickle
import pytest


PROD_SPREADSHEET_ID = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

TEST_SPREADSHEET_ID = "1UDLGeqhVxfHJF5zk2EWRnWuQrZLQkCbwdg9loyd1nFg"

# TODO: reduce api calls with class scope of dummy service

# TODO: create test for throttle

# TODO: replace pytest-freezegun with just freezegun maybe?


@pytest.fixture(scope="function")
def dummy_service():
    """create consistent testing spreadsheet and yield service"""
    credential_path = "./token.pickle"
    with open(credential_path, "rb") as token:
        creds = pickle.load(token)

    service = build("sheets", "v4", credentials=creds)

    # TODO: refactor, extract  and generalize the sheet standardization
    service.spreadsheets().values().clear(
        spreadsheetId=TEST_SPREADSHEET_ID, range="terms!A:Z"
    ).execute()
    service.spreadsheets().values().clear(
        spreadsheetId=TEST_SPREADSHEET_ID, range="buckets!A:Z"
    ).execute()

    buckets_values = [
        ["card_id", "timestamp_tested", "bucket_after_test"],
        [1, 1577865600, 1],  # 2020-01-01 08:00:00
        [2, 1577865660, 2],  # 2020-01-01 08:01:00
    ]

    terms_values = [
        ["card_id", "front", "back"],
        [1, "Capital of France?", "Paris"],
        [2, "Square root of four?", "Two"],
        [3, "How many legs does a horse have?", "Four"],
    ]

    body = {"values": terms_values}
    service.spreadsheets().values().update(
        spreadsheetId=TEST_SPREADSHEET_ID,
        range="terms!A:C",
        body=body,
        valueInputOption="RAW",
    ).execute()

    body = {"values": buckets_values}
    service.spreadsheets().values().update(
        spreadsheetId=TEST_SPREADSHEET_ID,
        range="buckets!A:C",
        body=body,
        valueInputOption="RAW",
    ).execute()

    return service


def test_get_terms(dummy_service):
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    result = ff.get_terms()
    assert result.shape == (3, 2)
    assert result.iloc[0]["back"] == "Paris"
    assert result.iloc[2]["front"] == "How many legs does a horse have?"


def test_get_buckets(dummy_service):
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    result = ff.get_buckets()

    assert result.values.tolist() == [
        ["1", "1577865600"],
        ["2", "1577865660"],
    ]


@pytest.mark.parametrize(
    "date,expected",
    [
        ("2020-01-01 08:00:00", ["1"]),
        ("2020-01-01 22:00:00", ["1"]),
        ("2020-01-02 08:00:00", ["1", "2"]),
        ("2020-01-11 14:34:25", ["1"]),
        ("2020-01-16 14:34:25", ["1", "2"]),
        ("2020-01-18 14:34:25", ["1", "2", "3", "5"]),
        ("2020-01-20 14:34:25", ["1", "2", "4"]),
    ],
)
def test_todays_buckets(date, expected, freezer):
    # assuming a ff.start_date of 2019-12-31
    with freeze_time(date, tick=True):
        ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
        result = ff._todays_buckets()
        assert result == expected


@pytest.mark.parametrize(
    "date,expected",
    [("2020-01-01 10:00:00", ["3"]), ("2020-01-02 10:00:00", ["1", "2", "3"]),],
)
def test_todays_cards(dummy_service, freezer, date, expected):
    # assuming a ff.start_date of 2019-12-31 (and in the sheet)
    with freeze_time(date, tick=True):
        ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
        result = ff.todays_cards()

        assert result == expected


@freeze_time("2020-01-02 08:34:26", tick=True)
@pytest.mark.parametrize(
    "card,success,expected",
    [
        ("1", True, [["1", "2", "1577954066"], ["2", "2", "1577865660"]]),
        ("2", False, [["1", "1", "1577865600"], ["2", "1", "1577954066"]]),
        (
            "3",
            False,
            [
                ["1", "1", "1577865600"],
                ["2", "2", "1577865660"],
                ["3", "1", "1577954066"],
            ],
        ),
        (
            "3",
            True,
            [
                ["1", "1", "1577865600"],
                ["2", "2", "1577865660"],
                ["3", "2", "1577954066"],
            ],
        ),
    ],
)
def test_update_bucket(card, success, expected, freezer, dummy_service):
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    ff.update_bucket(card, success)
    # FIXME: After adding the throttle decorator it meant that we had to
    # introduce a ticking time freeze. Hence we cannot be exactly certain of
    # the expected times. This test should be refactored because now it is
    # disgusting...
    new_buckets = ff.get_buckets()
    result = new_buckets.reset_index().values.tolist()
    result_times = [int(row[-1]) for row in result]
    expected_times = [int(row[-1]) for row in expected]

    for idx in range(len(result_times)):
        assert result_times[idx] - expected_times[idx] < 10

    assert [row[:-1] for row in result] == [row[:-1] for row in expected]


def test_add_term(dummy_service):
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    ff.add_term(
        front="What should horses in training wear in the stable?", back="A Blanket",
    )

    assert ff.get_terms().values[-1].tolist() == [
        "What should horses in training wear in the stable?",
        "A Blanket",
    ]


def test_functional(dummy_service, freezer):
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)

    first_test_date = datetime.datetime(2020, 1, 2, 8)
    for day in range(len(tests[0])):
        datetime_offset = datetime.timedelta(days=day)
        with freeze_time(first_test_date + datetime_offset, tick=True):

            if day in terms_to_add:
                for _ in range(terms_to_add[day]):
                    ff.add_term("front", "back")
                    # making sure the cards we are going to test are in the correct buckets

            todays_cards = ff.todays_cards()
            todays_tests = [test[day] for test in tests]
            for card in todays_cards:
                card_idx = int(card) - 1

                assert todays_tests[card_idx] is not None

            # test the cards
            for card in range(1, 7):
                test_result = tests[card - 1][day]
                if test_result is not None:
                    ff.update_bucket(str(card), test_result)

            # assert the buckets
            buckets_df = ff.get_buckets()
            assert buckets_df["bucket_after_test"].tolist() == [
                str(card[day + 1]) for card in buckets if card[day + 1] != 0
            ]
