# from http import server
from ..server import create_app
import pytest
from importlib import reload

# @pytest.fixture
# def app_fixture():
    
#     yield create_app({"TESTING":True})
@pytest.fixture
def app_fixture():
    yield create_app({"TESTING":True})


@pytest.fixture(scope="function")
def client(app_fixture):
    with app_fixture.test_client() as client:
        yield client


