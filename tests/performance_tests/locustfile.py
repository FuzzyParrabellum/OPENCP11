from datetime import datetime
import json

from locust import HttpUser, task

from server import CLUB_FILE, COMP_FILE


class ProjectPerfTest(HttpUser):

    def on_start(self):

        with open("{}".format(CLUB_FILE), "r") as jsonFile:
            self.clubs = json.load(jsonFile)

        with open("{}".format(COMP_FILE), "r") as jsonFile:
            self.competitions = json.load(jsonFile)

        format_string = "%Y-%m-%d %H:%M:%S"
        test_time = "2015-03-27 10:00:00"
        self.test_time = datetime.strptime(test_time, format_string)
        self.current_time = datetime.now().strftime(format_string)


    @task
    def index(self):
        self.client.get("/")

    @task
    def showSummary(self):
        response = self.client.post('/showSummary', data={'email':'john@simplylift.co'})

    @task
    def book(self):
        test_club_name = self.clubs['clubs'][0]['name']
        test_comp_name = self.competitions['competitions'][0]['name']
        response = self.client.get(f'/book/{test_comp_name}/{test_club_name}')

    @task
    def purchasePlaces(self):

        test_club = self.clubs['clubs'][0]['name']
        test_comp = self.competitions['competitions'][0]['name']
        places_to_buy = 1
        response = self.client.post('/purchasePlaces', data={'competition': test_comp,
                                                        'club': test_club,
                                                        'places':places_to_buy,
                                                        'optionnal_time':self.test_time})

    @task
    def displayClubs(self):
        self.client.get('/displayBoard', data={'clubs':self.clubs['clubs']})

    @task
    def logout(self):
        self.client.get('/logout')
