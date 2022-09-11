from ..conftest import client
from ..conftest import app_fixture as app
import pytest
from Python_Testing.server import loadClubs, loadCompetitions
from flask import url_for, request, Flask


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
    
    def test_should_accept_right_emails(self, client):
        # Ici on pourrait utiliser parametrize ET la 1ere fixture pour récupérer tous
        # les emails et les essayer un à un pour voir si ça marche, que le status_code
        # est bon et qu'on est bien redirigé vers la bonne page html

        response = client.post('/showSummary', data={'email':'john@simplylift.co'})
        assert response.status_code == 200

    # DECOMMENTER A LA FIN
    # def test_should_redirect_wrong_email(self, client):
    #     # il faut indiquer ce qui se passe quand on entre un mauvais email, pour l'instant
    #     # fait planter l'appli, il faudrait plutôt que ça renvoie un msg d'erreur et qu'on
    #     # revienne sur l'index je pense
    #     response = client.post('/showSummary', data={'email':'test@wrong-email.co'})
    #     assert response.headers["Location"] == "/"

class TestBookCompetition():

    # Pouurait peut-etre mettre une methode setup et teardown pour ne pas avoir
    # a réécrire le code des good_club et bad_club 
    
    def test_should_error_if_club_or_comp_not_found(self, client, Competitions_Fixture, 
                                                    Clubs_Fixture):
        good_comp_name = Competitions_Fixture[0]['name']
        bad_comp = {"name":"test_name", "date":"2020-03-27 10:00:00", 
                    "numberOfPlaces":"24"}
        bad_comp_name = bad_comp['name']
        good_club_name = Clubs_Fixture[0]['name']
        bad_club = {"name":"test_name", "email":"test@example.com", "points":"25"}
        bad_club_name = bad_club['name']
        response1 = client.get(f'/book/{bad_comp_name}/{good_club_name}')
        response2 = client.get(f'/book/{good_comp_name}/{bad_club_name}')
        # mettre egalement un assert de redirection
        # apparement peut mettre 
        assert response1.status_code == 500
        assert response2.status_code == 500

    def test_should_connect_to_right_html(self, client, Competitions_Fixture, 
                                                    Clubs_Fixture):
        # ici peut-être à la fois mettre le test de la bonne html mais aussi du bon
        # status_code
        good_comp_name = Competitions_Fixture[0]['name']
        good_club_name = Clubs_Fixture[0]['name']
        response = client.get(f'/book/{good_comp_name}/{good_club_name}')
        assert response.status_code == 200


class TestPurchase():
    
    def test_should_buy_places(self, client):
        # Il faut ici vérifier que si on envoie un club, un festival et un nb de places,
        # en fonction du nombre de places dans le fichier json competitions
        # et du nombre de points du club (prévoir un multiplieur de nb de points 
        # nécessaire) dans le fichier json clubs, il y a 
        # 1 une bonne redirection
        # 2 un nombre de points déduit du club
        # 3 un nombre de place déduit de la competition

        # Il faut penser à mocker : renvoyer une constance qui sera installée
        # ensuite dans views qui est le nombre de points nécessaires pour booker
        # une compétition.
        data = {"competition":'Spring Festival', "club":"Simply Lift", "places":"1"}
        response = client.post('/purchasePlaces', data=data)
        assert response.status_code == 200

    def test_enough_place_in_competition_to_book(self, client, Competitions_Fixture, 
                                        Clubs_Fixture):
        
        test_comp = Competitions_Fixture[0]
        test_club = Clubs_Fixture[0]
        places_to_buy = 1
        # here is the value of a ticket mais devrait plutôt être dans server.py en fait

        ticket_value = 1
        places_to_buy = places_to_buy*ticket_value

        # Il faudrait ici modifier cette reponse et ce client.post pour que 
        # l'information passe plutôt dans notre test et pas la view,
        # ou alors qu'on puisse mocker le comportement de la view et donc l'écriture
        # du fichier ensuite
        response = client.post('/purchasePlaces', data={"competition": test_comp[0],
                                                        "club": test_club[0],
                                                        "places":places_to_buy})
        # on vérifie 1 qu'il reste des places 2 qu'il reste assez de places pour
        # le nombre de places que le club veut acheter 3 que le club a assez de points
        # pour acheter ce nombre de places

        # on vérifie ensuite que le fichier json a bien été réécris si il le nombre
        # de places et de points était correct
        # Pour se faire je peux créer dans server.py les fonctions rewriteClubs et
        # rewriteCompetitions que je peux importer ici en fixture avec en + les 
        # fonctions loadClubs et loadCOmpetitions, utiliser les fonctions load avec
        # ma fixture du fichier json et utiliser les fonctions rewrite avec cela

        # Test 2 - vérification nombre de points suffisants pour booker
        # A) on voit en paramètre le nom du club, celui de la compétition et le nombre
        # de places que le club veut booker
        # B) on a en fixture le nombre de points nécessaires pour booker une compétition
        # ou on l'importe à partir de views
        # Bbis) pour la résolution du bug, trouver le nombre de points dont dispose
        # un club en variable + trouver aussi variable du nbre de place competition
        # C) si le il n'y a plus de places disponibles dans la compétition, on ne 
        # devrait pas pouvoir booker le club, l'assert
        # D) si le club n'a pas assez de points pour booker le nombre de places qu'il veut
        # il ne doit pas non plus pouvoir le faire, l'assert, mettre dans la correction
        # du bug le nombre de points qu'il manque au club pour pouvoir booker une place
        
        # Test 3 - impossibilité de booker plus de N places pour un club
        # A) à partir de la variable N, ici mise à 12
        # B) on assert que si le secrétaire essaie d'en booker plus de 12, alors il est
        # renvoyé sur la page d'avant avec un message d'erreur

        # Test 4 - impossibilité de booker une compétition si elle a lieu dans le passé
        # QUESTION PROF : toutes les compétitions du fichier json ont eu lieu dans le
        # passé, que faire à la fin du test donc ? Indiquer une constante avec la date
        # qui est supposée être présente ?
        # A) On met une date en constance qui indique la date actuelle
        # B) Le programe checke si la date de la compétition est passée ou future,
        # et continue l'opération si elle est future, arrête l'opération et redirige
        # avec un message d'erreur si elle est passée




class TestLogout():

    def test_logout_and_redirect(self, client):
        
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200





