from reporting.deck import Deck
import pytest
from tests.fixtures import generate_dummy_service

# TODO: BNPR centralize these constant values... conftest?
PROD_SPREADSHEET_ID = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

TEST_SPREADSHEET_ID = "1UDLGeqhVxfHJF5zk2EWRnWuQrZLQkCbwdg9loyd1nFg"

@pytest.mark.skip(reason="wip")
def test_deck_from_dataframe(generate_dummy_service):
    dummy_service = generate_dummy_service(buckets_values="blah", terms_values="blooh")
    ff = flippyflop.FlippyFlop(dummy_service, TEST_SPREADSHEET_ID)
    df = ff.get_buckets()
     
    deck = Deck.from_df(df)

    assert "the deck is what we expect it to be"
