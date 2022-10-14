import pytest

from ..server import create_app


@pytest.fixture
def app_fixture():
    """Create the app_fixture that will next be used to get the application context
    for the unit tests"""
    yield create_app({"TESTING":True})


@pytest.fixture(scope="function")
def client(app_fixture):
    """Create the client fixture that will next be used to test the app's endpoints"""
    with app_fixture.test_client() as client:
        yield client
