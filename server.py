import json, pdb
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime


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
    with open(CLUB_FILE) as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open(COMP_FILE) as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions

competitions = loadCompetitions()
clubs = loadClubs()


def can_purchase(club, competition, num_places, place_value, app_time=CURRENT_TIME):
    # helper function pour la route suivante, /purchasePLaces, permet de déterminer
    # si un club peut acheter un nombre de places donné à une compétition donnée

    format_string = "%Y-%m-%d %H:%M:%S"
    competition_time = datetime.strptime(competition["date"], format_string)
    if type(app_time) != type(competition_time):
        app_time = datetime.strptime(app_time, format_string)
    new_places = num_places*place_value
    if int(club["points"]) < new_places:
        flash("Your club doesn't have enough points to book this number of places")
        return False
    elif (int(competition['numberOfPlaces']) - num_places) < 0:
        flash("There is not enough places left to book this number of places")
        return False
    elif app_time > competition_time:
        flash("This competition is already over, you can't book it")
        return False
    else:
        return True

def get_clubs():
    print(clubs)

# def find_list_of_dict_index(list_of_dict, name):
#     index = 0
#     for dict in list_of_dict:
#         if name in dict.values():
#             return index
#         index += 1

PLACE_VALUE = 1

def create_app(config={}):
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = 'something_special'

    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/showSummary',methods=['POST'])
    def showSummary():
        for club in clubs:
            if club['email'] == request.form['email']:
                return render_template('welcome.html',club=club,competitions=competitions)
        flash("There wasn't any club with this email in our database")
        return redirect(url_for('index'))

    # class ParametersError(Exception):
    #     code = 400
    #     description = "You didn't put an existing club in the parameters of you request!"

    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        try:
            foundClub = [c for c in clubs if c['name'] == club][0]
            foundCompetition = [c for c in competitions if c['name'] == competition][0]
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        # if foundClub and foundCompetition:
        except:
            return f"""You didn't put an existing club or competition in the 
            parameters of you request! Your parameters were {competition}/{club}""", 400
            # raise ParametersError(f"""You didn't put an existing club or competition in the 
            # parameters of you request! Your parameters were {competition}/{club}""")
        # elif foundClub:
        #     flash("Something went wrong-please try again")
        #     return render_template('welcome.html', club=club, competitions=competitions)
        # else:
            
    # Ici que j'avais mis anciennement can_purchase

    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]
        global CURRENT_TIME
        # mettre ce global est nécessaire pour pouvoir mettre la condition ci_dessous, sinon
        # bug
        if request.form['optionnal_time'] != "FALSE":
            CURRENT_TIME = request.form['optionnal_time']
        placesRequired = int(request.form['places'])
        if placesRequired > 12:
            flash("you can't book more than twelve places at once !")
            print("YES")
            return render_template('welcome.html', club=club, competitions=competitions)
        if can_purchase(club, competition, placesRequired, PLACE_VALUE, CURRENT_TIME):
            print("NO")
            club["points"] = str(int(club["points"]) - placesRequired*PLACE_VALUE)
            competition_to_deduct = competitions[competitions.index(competition)]
            competition_to_deduct["numberOfPlaces"] = \
                str(int(competition_to_deduct["numberOfPlaces"]) - placesRequired)
            flash('Great-booking complete!')
        # competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        return render_template('welcome.html', club=club, competitions=competitions)


    # TODO: Add route for points display
    @app.route('/displayBoard',methods=['GET'])
    def displayBoard():
        return render_template('display_board.html', clubs=clubs)

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app

# if __name__ == "__main__":
#     app.run(debug=True)
