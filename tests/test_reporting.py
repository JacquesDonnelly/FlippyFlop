from reporting.deck import Deck, Schedule, Card
import pytest
from tests.fixtures import generate_dummy_service
import datetime
from app import flippyflop

# TODO: BNPR centralize these constant values... conftest?
PROD_SPREADSHEET_ID = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

TEST_SPREADSHEET_ID = "1UDLGeqhVxfHJF5zk2EWRnWuQrZLQkCbwdg9loyd1nFg"


def test_deck_from_dataframe(generate_dummy_service):
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
    dummy_service = generate_dummy_service(
        buckets_values=buckets_values, terms_values=None
    )
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    df = ff.get_all_buckets()
    deck = Deck.from_df(df)

    assert len(deck.cards) == 6
    assert deck.card_by_id(1).test_dates == [
        datetime.datetime(2020,1,4,19,32),
        datetime.datetime(2020,1,5,19,32)
    ]
    assert deck.card_by_id(2).results == [True, True]
    assert deck.card_by_id(3).results == [True]
    assert deck.card_by_id(4).results == [False, True]
    assert deck.card_by_id(5).results == [True, False]
    assert deck.card_by_id(6).test_dates == [
        datetime.datetime(2020, 1, 4, 20, 1)
    ]


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
        (
            2,
            {
                "results": [False],
                "test_dates": [
                    datetime.datetime(2020, 1, 1, 8),
                ],
            },
        ),
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

