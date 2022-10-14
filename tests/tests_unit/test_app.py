"""Unitary_test module for the project"""

import re
import json
from datetime import datetime

import pytest
from Python_Testing.server import loadClubs, loadCompetitions, \
    CLUB_FILE, COMP_FILE, can_purchase
from ..conftest import app_fixture as app


@pytest.fixture
def clubs_fixture():
    """Fixture for the clubs.json file used as a database for the project"""

    data = [{"name":"Simply Lift","email":"john@simplylift.co",
        "points":"13"},
        {"name":"Iron Temple","email": "admin@irontemple.com",
        "points":"4"},
        {"name":"She Lifts", "email": "kate@shelifts.co.uk",
        "points":"12"}]
    return data

@pytest.fixture
def competitions_fixture():
    """Fixture for the competitions.json file used as a database for the project"""

    data = [{"name": "Spring Festival","date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"},
            {"name": "Fall Classic","date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"}]
    return data

def test_load_clubs(clubs_fixture):
    """Checks if the loadClubs function from the server.py file returns the same
    data as the clubs.json file used as local database for this project"""

    list_of_clubs = loadClubs()
    assert list_of_clubs == clubs_fixture

def test_load_competitions(competitions_fixture):
    """Checks if the loadCompetitions function from the server.py file returns the same
    data as the competitions.json file used as local database for this project"""

    list_of_competitions = loadCompetitions()
    assert list_of_competitions == competitions_fixture


class TestIndex():

    """Class holding all the tests for the '/' route"""

    def test_should_status_code_ok(self, client):
        """Checks if user can connect to website login page"""

        response = client.get('/')
        assert response.status_code == 200


class TestSummary():

    """Class holding all the tests for the '/showSummary' route"""

    def test_should_accept_right_emails(self, client):
        """Checks that user can connect to homepage with right email"""

        response = client.post('/showSummary', data={'email':'john@simplylift.co'})
        assert response.status_code == 200

    def test_should_redirect_wrong_email(self, client):
        """Checks that user can't connect to homepage with wrong email"""

        response = client.post('/showSummary', data={'email':'test@wrong-email.co'})
        assert response.headers["Location"] == "/"

class TestBookCompetition():

    """Class holding all the tests for the '/book/<competition>/<club>' route"""

    def test_should_error_if_club_or_comp_not_found(self, client, competitions_fixture,
                                                    clubs_fixture):
        """Checks that website returns an error if someone tries to forcefully
        put wrong competition or club name as parameters when booking"""

        good_comp_name = competitions_fixture[0]['name']
        bad_comp = {"name":"test_name", "date":"2020-03-27 10:00:00", 
                    "numberOfPlaces":"24"}
        bad_comp_name = bad_comp['name']
        good_club_name = clubs_fixture[0]['name']
        bad_club = {"name":"test_name", "email":"test@example.com", "points":"25"}
        bad_club_name = bad_club['name']
        response1 = client.get(f'/book/{bad_comp_name}/{good_club_name}')
        response2 = client.get(f'/book/{good_comp_name}/{bad_club_name}')

        assert response1.status_code == 400
        assert response2.status_code == 400

    def test_should_connect_to_right_html(self, client, competitions_fixture,
                                                    clubs_fixture):
        """Checks that user can access booking page with right club name and 
        competition name"""

        good_comp_name = competitions_fixture[0]['name']
        good_club_name = clubs_fixture[0]['name']
        response = client.get(f'/book/{good_comp_name}/{good_club_name}')
        assert response.status_code == 200


class TestPurchase():

    """Class holding all the tests for the '/purchasePlaces' route"""

    def setup_method(self, method):
        """setup_method for saving the 4 variables self.clubs, self.competitions,
        self.test_time and self.current_time for the next tests"""

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
        """Checks that club's secretary can book a place in a competition and
        that the number of points used is deducted from the club balance"""

        test_comp = competitions_fixture[0]["name"]
        test_club = clubs_fixture[0]["name"]
        places_to_buy = 1
        ticket_value = 3


        response = client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})
        assert response.status_code == 200

        points_regex = re.compile(r'(Points available: )(\d+)')
        response_html = response.data.decode()
        mo = points_regex.search(response_html)
        original_club_points = int(self.clubs["clubs"][0]["points"])

        assert original_club_points - (places_to_buy*ticket_value) == int(mo.group(2))


    def test_enough_places_left_to_book(self, client, competitions_fixture,
                                        clubs_fixture):
        """Checks that a club's secretary can't book more places than the competition's
        number of places, the competitions balance should remain the same"""

        test_comp = competitions_fixture[0]["name"]
        test_club = clubs_fixture[0]["name"]
        places_to_buy = 500

        response = client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})
        assert response.status_code == 200

        places_regex = \
            re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
        response_html = response.data.decode()
        mo = places_regex.search(response_html)
        original_comp_places = int(self.competitions["competitions"][0]["numberOfPlaces"])

        assert original_comp_places == int(mo.group(2))

    def test_competition_isnt_expired(self, client, competitions_fixture,
                                        clubs_fixture, app):
        """Checks that you can't book an expired competition and that you can book
        a future competition"""

        test_comp = competitions_fixture[0]
        test_club = clubs_fixture[0]
        places_to_buy = 1
        ticket_value = 3

        later_date_comp = {
            "name": "Lalapalooza Festival",
            "date": "2025-03-27 10:00:00",
            "numberOfPlaces": "25"
        }

        with app.app_context():
            purchase_with_past_date = can_purchase(test_club, test_comp, places_to_buy, \
                                                    ticket_value)
            purchase_with_later_date = can_purchase(test_club, later_date_comp, \
                                        places_to_buy, ticket_value)

            assert purchase_with_past_date is False
            assert  purchase_with_later_date is True

        response = client.post('/purchasePlaces', data={'competition': test_comp["name"],
                                                        'club': test_club["name"],
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.current_time})

        html_content = response.data.decode()

        assert "This competition is already over" in html_content


    def test_competitions_places_can_get_deducted(self, client, competitions_fixture, 
                                    clubs_fixture):
        """Checks that places are deducted from a competition balance"""

        test_comp = competitions_fixture[0]["name"]
        test_club = clubs_fixture[0]["name"]
        places_to_buy = 1

        response = client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})
        assert response.status_code == 200

        places_regex = \
            re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
        response_html = response.data.decode()
        mo = places_regex.search(response_html)
        original_comp_places = int(self.competitions["competitions"][0]["numberOfPlaces"])
        assert original_comp_places - places_to_buy == int(mo.group(2))

    def test_cant_book_more_than_twelve_places(self, client, competitions_fixture,
                                    clubs_fixture):
        """Checks that a club's secretary can't book more than 12 places at once"""

        test_comp = competitions_fixture[0]["name"]
        test_club = clubs_fixture[0]["name"]
        places_to_buy = 13

        # Verify in front-end that user can't select more than 12 places
        response = client.get(f'/book/{test_comp}/{test_club}')
        data = response.data.decode()
        assert '<input type="number" name="places" min="1" max="12" id=""/>' in data

        # Verify in back-end that purchasing more than 12 places at once isn't possible,
        # and that competitions places aren't deducted
        response = client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})
        assert response.status_code == 200

        places_regex = \
            re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
        response_html = response.data.decode()
        mo = places_regex.search(response_html)
        original_comp_places = int(self.competitions["competitions"][0]["numberOfPlaces"])

        assert original_comp_places == int(mo.group(2))

class TestLogout():

    """Class holding all the tests for the '/logout' route"""

    def test_logout_and_redirect(self, client):
        """Checks that the /logout route redirects user to index"""

        response = client.get('/logout')
        assert response.status_code == 302
