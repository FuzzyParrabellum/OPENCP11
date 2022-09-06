from ..conftest import client
import pytest
from Python_Testing.server import loadClubs, loadCompetitions

# Fixture des Clubs et des Compétitions
@pytest.fixture
def Clubs_Fixture():
    data = [{'name': 'Simply Lift', 'email': 'john@simplylift.co', 'points': '13'}, 
    {'name': 'Iron Temple', 'email': 'admin@irontemple.com', 'points': '4'}, 
    {'name': 'She Lifts', 'email': 'kate@shelifts.co.uk', 'points': '12'}]
    return data

@pytest.fixture
def Competitions_Fixture():
    data = [{"name": "Spring Festival","date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"},
            {"name": "Fall Classic","date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"}]
    return data
    
# Test des fonctions LoadClubs et LoadCompetions pour voir si on a bien la bonne data
def test_loadClubs(Clubs_Fixture):
    list_of_clubs = loadClubs()
    assert list_of_clubs == Clubs_Fixture

def test_loadCompetitions(Competitions_Fixture):
    list_of_competitions = loadCompetitions()
    assert list_of_competitions == Competitions_Fixture

# Tests de l'index, organiser ça en Classe ?
# Avec une Classe par route ?


class TestIndex():

    # def __init__(self, client):
    #     self.client = client

    # Test pour montrer que la route est accessible
    def test_should_status_code_ok(self, client):
        response = client.get('/')
        assert response.status_code == 200


class TestSummary():
    
    def test_should_accept_right_emails(client):
        # Ici on pourrait utiliser parametrize ET la 1ere fixture pour récupérer tous
        # les emails et les essayer un à un pour voir si ça marche, que le status_code
        # est bon et qu'on est bien redirigé vers la bonne page html

        response = client.post('/showSummary', data={'email':'john@simplylift.co'})
        assert response.status_code == 200


    def test_should_redirect_wrong_email(client):
        # il faut indiquer ce qui se passe quand on entre un mauvais email, pour l'instant
        # fait planter l'appli, il faudrait plutôt que ça renvoie un msg d'erreur et qu'on
        # revienne sur l'index je pense
        response = client.post('/showSummary', data={'email':'test@wrong-email.co'})
        assert response.headers["Location"] == "/"






# class TestBookCompetition(Clubs_Fixture, Competitions_Fixture):
#     pass

# class TestPurchase(Clubs_Fixture, Competitions_Fixture):
#     pass