import os
import tempfile

import pytest

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_sandbox(client):
    rv = client.get('/')

    assert 0
