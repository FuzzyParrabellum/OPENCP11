from http import server
from ..server import app
import pytest

@pytest.fixture
def app_fixture():
    yield app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client