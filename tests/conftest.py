import pytest

from ..server import create_app


@pytest.fixture
def app_fixture():
    """Crée la fixture app_fixture qui sera ensuite utilisée pour utiliser le
    contexte de l'application dans les tests"""
    yield create_app({"TESTING":True})


@pytest.fixture(scope="function")
def client(app_fixture):
    """Crée la fixture client qui sera utilisée pour tester les endpoints de
    l'application dans les tests"""
    with app_fixture.test_client() as client:
        yield client
