import json
from datetime import datetime

from flask import Flask,render_template,request,redirect,flash,url_for



# If you want to set the current_time to now
CURRENT_TIME = datetime.now()
# If you want to set the current_time to before the competitions in the json file,
# you need to set it before "2020-03-27 10:00:00"
# format_string = "%Y-%m-%d %H:%M:%S"
# test_time = "2015-03-27 10:00:00"
# CURRENT_TIME = datetime.strptime(test_time, format_string)

CLUB_FILE = "clubs.json"
COMP_FILE = "competitions.json"


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def can_purchase(club, competition, num_places, place_value, app_time=CURRENT_TIME):
    # helper function pour la route suivante, /purchasePLaces, permet de déterminer
    # si un club peut acheter un nombre de places donné à une compétition donnée

    format_string = "%Y-%m-%d %H:%M:%S"
    competition_time = datetime.strptime(competition["date"], format_string)
    if type(app_time) != type(competition_time):
        app_time = datetime.strptime(app_time, format_string)
    elif app_time > competition_time:
        flash("This competition is already over, you can't book it")
        return False
    else:
        return True

PLACE_VALUE = 1

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    global CURRENT_TIME
        # mettre ce global est nécessaire pour pouvoir mettre la condition ci_dessous, 
        # sinon bug
    if request.form['optionnal_time'] != "FALSE":
        CURRENT_TIME = request.form['optionnal_time']
    placesRequired = int(request.form['places'])
    if can_purchase(club, competition, placesRequired, PLACE_VALUE, CURRENT_TIME):
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
