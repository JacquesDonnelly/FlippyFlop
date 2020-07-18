import pytest

from app.routes import generate_remaining_cards_phrase

@pytest.mark.parametrize("remaining_cards,expected", [(1, "1 Card Remaining"), (55, "55 Cards Remaining")])
def test_card_footer_generation(remaining_cards, expected):
    result = generate_remaining_cards_phrase(remaining_cards)

    assert result == expected
