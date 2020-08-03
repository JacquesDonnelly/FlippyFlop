from reporting.deck import Deck, Schedule, Card
import pytest
from freezegun import freeze_time
from tests.fixtures import generate_dummy_service
import datetime
from app import flippyflop

# TODO: BNPR centralize these constant values... conftest?
PROD_SPREADSHEET_ID = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

TEST_SPREADSHEET_ID = "1UDLGeqhVxfHJF5zk2EWRnWuQrZLQkCbwdg9loyd1nFg"


@pytest.fixture
def dummy_deck(generate_dummy_service):
    buckets_values = [
        ["card_id", "timestamp_tested", "bucket_after_test"],
        [1, 1578166320, 1],  # "2020-01-04 19:32:00"
        [2, 1578166444, 2],  # "2020-01-04 19:34:04"
        [3, 1578166517, 2],  # "2020-01-04 19:35:17"
        [4, 1578166560, 1],  # "2020-01-04 19:36:00"
        [5, 1578168060, 2],  # "2020-01-04 20:01:00"
        [6, 1578168060, 1],  # "2020-01-04 20:01:00"
        [1, 1578252720, 1],  # "2020-01-05 19:32:00"
        [2, 1578252844, 3],  # "2020-01-05 19:34:04"
        [4, 1578252960, 2],  # "2020-01-05 19:36:00"
        [5, 1578254460, 1],  # "2020-01-05 20:01:00"
    ]
    terms_values = [
        ["card_id", "front", "back"],
        [1, "Capital of France?", "Paris"],
        [2, "Square root of four?", "Two"],
        [3, "How many legs does a horse have?", "Four"],
        [4, "Capital of England?", "London"],
        [5, "Square root of nine?", "Three"],
        [6, "How many legs does a woman have?", "Two"],
    ]
    dummy_service = generate_dummy_service(
        buckets_values=buckets_values, terms_values=terms_values
    )
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    df = ff.get_all_buckets()
    deck = Deck.from_df(df)
    return deck


def test_deck_from_dataframe(dummy_deck):

    assert len(dummy_deck.cards) == 6
    assert dummy_deck.card_by_id(1).test_dates == [
        datetime.datetime(2020, 1, 4, 19, 32),
        datetime.datetime(2020, 1, 5, 19, 32),
    ]
    assert dummy_deck.card_by_id(2).results == [True, True]
    assert dummy_deck.card_by_id(3).results == [True]
    assert dummy_deck.card_by_id(4).results == [False, True]
    assert dummy_deck.card_by_id(5).results == [True, False]
    assert dummy_deck.card_by_id(6).test_dates == [datetime.datetime(2020, 1, 4, 20, 1)]


@pytest.mark.parametrize(
    "_id,expected",
    [
        (
            1,
            {
                "results": [True, True],
                "test_dates": [
                    datetime.datetime(2020, 1, 1, 8),
                    datetime.datetime(2020, 1, 1, 9),
                ],
            },
        ),
        (2, {"results": [False], "test_dates": [datetime.datetime(2020, 1, 1, 8),],},),
    ],
)
def test_card_by_id(_id, expected):
    cards = [
        Card(
            _id=1,
            results=[True, True],
            test_dates=[
                datetime.datetime(2020, 1, 1, 8),
                datetime.datetime(2020, 1, 1, 9),
            ],
        ),
        Card(_id=2, results=[False], test_dates=[datetime.datetime(2020, 1, 1, 8),],),
    ]
    schedule = Schedule()
    deck = Deck(cards, schedule)

    card = deck.card_by_id(_id)

    assert card.results == expected["results"]
    assert card.test_dates == expected["test_dates"]


# TODO: NEXT. Check these dates, the dates above and the day_zero in schedule
@pytest.mark.parametrize(
    "date,expected",
    [
        ("2020-01-01 09:55:00", 6),
        ("2020-01-02 10:02:30", 6),
        ("2020-01-03 05:02:30", 4),
    ],
)
def test_deck_count_to_be_tested_today(dummy_deck, date, expected):
    with freeze_time(date):
        result = dummy_deck.count_to_be_tested_today()

    assert result == expected


@pytest.mark.parametrize(
    "results,expected",
    [
        (
            [True, True],
            3,
        ),
        (
            [False, False, False, True],
            2,
        ),
        (
            [False, True, False, True, True],
            3,
        ),
        (
            [True, True, True, True, True, True],
            5,
        ),
    ],
)
def test_card_current_bucket(results, expected):
    test_dates = [
        datetime.datetime(2020, 1, 1) + datetime.timedelta(days=i)
        for i in range(len(results))
    ]
    card = Card(_id=420, results=results, test_dates=test_dates)

    with freeze_time(test_dates[-1] + datetime.timedelta(minutes=5)):
        assert card.current_bucket == expected
