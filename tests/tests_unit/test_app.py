"""Unitary_test module for the project"""

import pdb
import re
import json
from datetime import datetime
import importlib

from flask import session, current_app
import pytest
from Python_Testing.server import loadClubs, loadCompetitions, get_clubs,\
    CLUB_FILE, COMP_FILE, can_purchase
    # a arranger pour le app_context
# from ..conftest import app_fixture as app
# from ..conftest import client
# from flask import url_for, request, Flask




# Fixture des Clubs et des Compétitions
@pytest.fixture
def clubs_fixture():
    """Fixture for the clubs.json file used as a batabase for the project"""

    data = [{"name":"Simply Lift","email":"john@simplylift.co",
        "points":"13"},
        {"name":"Iron Temple","email": "admin@irontemple.com",
        "points":"4"},
        {"name":"She Lifts", "email": "kate@shelifts.co.uk",
        "points":"12"}]
    return data

@pytest.fixture
def competitions_fixture():
    """Fixture for the competitions.json file used as a batabase for the project"""

    data = [{"name": "Spring Festival","date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"},
            {"name": "Fall Classic","date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"}]
    return data

# Test des fonctions LoadClubs et LoadCompetions pour voir si on a bien la bonne data
# def test_load_clubs(clubs_fixture):
#     """Test vérifiant que la fonction loadCLubs utilisée dans server.py renvoie bien les données
#     du fichier clubs.json"""

#     list_of_clubs = loadClubs()
#     assert list_of_clubs == clubs_fixture

# def test_load_competitions(competitions_fixture):
#     """Test vérifiant que la fonction loadCompetitions utilisée dans server.py renvoie
#     bien les données du fichier clubs.json"""
#     list_of_competitions = loadCompetitions()
#     assert list_of_competitions == competitions_fixture

# # Tests de l'index, organiser ça en Classe ?
# # Avec une Classe par route ?


# class TestIndex():

#     """Classe effectuant tous les tests de la route '/'"""

#     # Test pour montrer que la route est accessible
#     def test_should_status_code_ok(self, client):
#         """Test pour savoir si l'utilisateur peut bien se connecter à l'index du site"""

#         response = client.get('/')
#         assert response.status_code == 200


# class TestSummary():

#     """Classe effectuant tous les tests de la route '/showSummary'"""

#     def test_should_accept_right_emails(self, client):
#         """Test pour vérifier qu'un utilisateur peut se connecter au site en 
#         indiquant un email valide"""

#         response = client.post('/showSummary', data={'email':'john@simplylift.co'})
#         assert response.status_code == 200

#     def test_should_redirect_wrong_email(self, client):
#         """Test pour vérifier qu'un utilisateur ne peut pas se connecter au site en 
#         indiquant un email invalide"""

#         response = client.post('/showSummary', data={'email':'test@wrong-email.co'})
#         assert response.headers["Location"] == "/"

# class TestBookCompetition():

#     """Classe effectuant tous les tests de la route '/book/<competition>/<club>'"""

#     def test_should_error_if_club_or_comp_not_found(self, client, competitions_fixture,
#                                                     clubs_fixture):
#         """Test vérifiant que le site renvoie bien une erreur quand on tente de renseigner
#         un mauvais nom de club ou de competition"""

#         good_comp_name = competitions_fixture[0]['name']
#         bad_comp = {"name":"test_name", "date":"2020-03-27 10:00:00", 
#                     "numberOfPlaces":"24"}
#         bad_comp_name = bad_comp['name']
#         good_club_name = clubs_fixture[0]['name']
#         bad_club = {"name":"test_name", "email":"test@example.com", "points":"25"}
#         bad_club_name = bad_club['name']
#         response1 = client.get(f'/book/{bad_comp_name}/{good_club_name}')
#         response2 = client.get(f'/book/{good_comp_name}/{bad_club_name}')

#         assert response1.status_code == 400
#         assert response2.status_code == 400

#     def test_should_connect_to_right_html(self, client, competitions_fixture,
#                                                     clubs_fixture):
#         """Test vérifiant qu'on peut bien se connecter au site en indiquant un bon nom de
#         competition et un bon nom de club"""

#         good_comp_name = competitions_fixture[0]['name']
#         good_club_name = clubs_fixture[0]['name']
#         response = client.get(f'/book/{good_comp_name}/{good_club_name}')
#         assert response.status_code == 200


class TestPurchase():

    """Classe effectuant tous les tests de la route '/purchasePlaces'"""

    def setup_method(self, method):
        """setup_method permettant d'enregistrer les 4 variables self.clubs, self.competitions,
        self.test_time et self.current_time pour les tests suivants"""

        with open(CLUB_FILE, "r") as json_file:
            self.clubs = json.load(json_file)

        with open(COMP_FILE, "r") as json_file:
            self.competitions = json.load(json_file)

        format_string = "%Y-%m-%d %H:%M:%S"
        test_time = "2015-03-27 10:00:00"
        self.test_time = datetime.strptime(test_time, format_string)
        self.current_time = datetime.now().strftime(format_string)



    def test_enough_points_to_book(self, client, competitions_fixture,
                                        clubs_fixture):
        """Test vérifiant que le secrétaire d'un club puisse acheter une place dans une compétition
        et que le nombre de points est bien déduit du portefeuille du club"""

        test_comp = competitions_fixture[0]["name"]
        test_club = clubs_fixture[0]["name"]
        places_to_buy = 1
        ticket_value = 1
        

        response = client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})
        assert response.status_code == 200

        # on vérifie que les points on bien été déduits
        points_regex = re.compile(r'(Points available: )(\d+)')
        response_html = response.data.decode()
        mo = points_regex.search(response_html)
        original_club_points = int(self.clubs["clubs"][0]["points"])

        assert original_club_points - (places_to_buy*ticket_value) == int(mo.group(2))

       
    def test_enough_places_left_to_book(self, client, competitions_fixture,
                                        clubs_fixture):
        """Test vérifiant que le secrétaire d'un club ne puisse pas acheter plus de places
        qu'il y en a dans la compétition"""
        
        test_comp = competitions_fixture[0]["name"]
        test_club = clubs_fixture[0]["name"]
        places_to_buy = 500
        ticket_value = 1
        
        # app = importlib.reload(client)
        # with client.session_transaction() as session
        #     pdb.set_trace()
        #     print('hello')
        # pdb.set_trace()
        
        # pdb.set_trace()
        # test_response = client.post('/showSummary', data={'email':'john@simplylift.co'})


        response = client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})
        assert response.status_code == 200
        # pdb.set_trace()
        # On s'assure que le nombre de places dans la compétition est toujours le même
        places_regex = \
            re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
        response_html = response.data.decode()
        mo = places_regex.search(response_html)
        original_comp_places = int(self.competitions["competitions"][0]["numberOfPlaces"])
        
        assert original_comp_places == int(mo.group(2))

    # def test_competition_isnt_expired(self, client, competitions_fixture,
    #                                     clubs_fixture, app):
    #     """Test vérifiant que la compétition à réserver n'est pas déjà passée, on utilise 
    #     late_date_comp pour voir si on peut réserver des places pour une compétition future"""

    #     test_comp = competitions_fixture[0]
    #     test_club = clubs_fixture[0]
    #     places_to_buy = 1
    #     ticket_value = 1

    #     later_date_comp = {
    #         "name": "Lalapalooza Festival",
    #         "date": "2025-03-27 10:00:00",
    #         "numberOfPlaces": "25"
    #     }

    #     with app.app_context():   
    #         purchase_with_past_date = can_purchase(test_club, test_comp, places_to_buy, \
    #                                                 ticket_value)
    #         purchase_with_later_date = can_purchase(test_club, later_date_comp, \
    #                                     places_to_buy, ticket_value)

    #         assert purchase_with_past_date is False
    #         assert  purchase_with_later_date is True

    #     response = client.post('/purchasePlaces', data={'competition': test_comp["name"],
    #                                                     'club': test_club["name"],
    #                                                     'places':places_to_buy,
    #                                                     'optionnal_time':self.current_time})

    #     html_content = response.data.decode() 

    #     assert "This competition is already over" in html_content


    # def test_competitions_places_can_get_deducted(self, client, competitions_fixture, 
    #                                 clubs_fixture):
    #     """Test vérifiant que le nombre de places d'une compétition diminue bien du
    #     nombre de places réservées par un club"""

    #     test_comp = competitions_fixture[0]["name"]
    #     test_club = clubs_fixture[0]["name"]
    #     places_to_buy = 1
    #     response = client.post('/purchasePlaces', data={'competition': test_comp,
    #                                                     'club': test_club,
    #                                                     'places':places_to_buy,
    #                                                     'optionnal_time':self.test_time})
    #     assert response.status_code == 200
    #     # on vérifie que les points on bien été déduits du fichier clubs.json
    #     # on vérifie que les points on bien été déduits du fichier
    #     places_regex = \
    #         re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
    #     response_html = response.data.decode()
    #     mo = places_regex.search(response_html)
    #     original_comp_places = int(self.competitions["competitions"][0]["numberOfPlaces"])
    #     assert original_comp_places - places_to_buy == int(mo.group(2))

    # def test_cant_book_more_than_twelve_places(self, client, competitions_fixture, 
    #                                 clubs_fixture):
    #     """Test vérifiant que le secrétaire d'un club de peut pas réserver plus de 12 places
    #     en une fois"""

    #     test_comp = competitions_fixture[0]["name"]
    #     test_club = clubs_fixture[0]["name"]
    #     places_to_buy = 13
        
    #     # Verify in front-end that user can't select more than 12 places
    #     response = client.get(f'/book/{test_comp}/{test_club}')
    #     data = response.data.decode()
    #     assert '<input type="number" name="places" min="1" max="12" id=""/>' in data

    #     # Verify in back-end that purchasing more than 12 places at once isn't possible,
    #     # and that competitions places aren't deducted
    #     response = client.post('/purchasePlaces', data={'competition': test_comp,
    #                                                     'club': test_club,
    #                                                     'places':places_to_buy,
    #                                                     'optionnal_time':self.test_time})
    #     assert response.status_code == 200

    #     places_regex = \
    #         re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
    #     response_html = response.data.decode()
    #     mo = places_regex.search(response_html)
    #     original_comp_places = int(self.competitions["competitions"][0]["numberOfPlaces"])

    #     assert original_comp_places == int(mo.group(2))

    # def teardown_method(self, method):
    #     with open("{}".format(CLUB_FILE), "r") as jsonFile:
    #         clubs_data = json.load(jsonFile)
        
    #     clubs_data["clubs"] = self.clubs["clubs"]

    #     with open("{}".format(CLUB_FILE), "w") as jsonFile:
    #         json.dump(clubs_data, jsonFile, indent=4)

    #     with open("{}".format(COMP_FILE), "r") as jsonFile:
    #         competitions_data = json.load(jsonFile)
        
    #     competitions_data["competitions"] = self.competitions["competitions"]

    #     with open("{}".format(COMP_FILE), "w") as jsonFile:
    #         json.dump(competitions_data, jsonFile, indent=4)

# class TestLogout():

#     """Classe effectuant tous les tests de la route '/logout'"""

#     def test_logout_and_redirect(self, client):
#         """Test vérifiant que la route /logout renvoie bien à la page d'acceuil"""

#         response = client.get('/logout', follow_redirects=True)
#         assert response.status_code == 200




# contenu de clubs.json
# {"clubs":[
#     {
#         "name":"Simply Lift",
#         "email":"john@simplylift.co",
#         "points":"13"
#     },
#     {
#         "name":"Iron Temple",
#         "email": "admin@irontemple.com",
#         "points":"4"
#     },
#     {   "name":"She Lifts",
#         "email": "kate@shelifts.co.uk",
#         "points":"12"
#     }
# ]}
