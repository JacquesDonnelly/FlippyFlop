import pytest

from main import generate_card_page_footer

@pytest.mark.parametrize("remaining_cards,expected", [(1, "1 Card Remaining"), (55, "55 Cards Remaining")])
def test_card_footer_generation(remaining_cards, expected):
    result = generate_card_page_footer(remaining_cards)

    assert result == expected
