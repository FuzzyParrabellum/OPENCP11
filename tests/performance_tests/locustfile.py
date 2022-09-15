# import sys  
# from pathlib import Path  
# file = Path(__file__).resolve()  
# package_root_directory = file.parents[2]  
# sys.path.append(str(package_root_directory))
# import sys
# print(sys.path)
from locust import HttpUser, task, constant
import json
from server import CLUB_FILE, COMP_FILE
from datetime import datetime

class ProjectPerfTest(HttpUser):

    def on_start(self):
        with open("{}".format(CLUB_FILE), "r") as jsonFile:
            clubs_data = json.load(jsonFile)
        self.clubs = clubs_data

        with open("{}".format(COMP_FILE), "r") as jsonFile:
            competitions_data = json.load(jsonFile)
        self.competitions = competitions_data

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
        # wait_time = constant(1)
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

    

    # @task
    # def logout(self):
    #     self.client.post('/logout')

    


    def on_stop(self):
        with open("{}".format(CLUB_FILE), "r") as jsonFile:
            clubs_data = json.load(jsonFile)
        
        clubs_data["clubs"] = self.clubs["clubs"]

        with open("{}".format(CLUB_FILE), "w") as jsonFile:
            json.dump(clubs_data, jsonFile, indent=4)

        with open("{}".format(COMP_FILE), "r") as jsonFile:
            competitions_data = json.load(jsonFile)
        
        competitions_data["competitions"] = self.competitions["competitions"]

        with open("{}".format(COMP_FILE), "w") as jsonFile:
            json.dump(competitions_data, jsonFile, indent=4)