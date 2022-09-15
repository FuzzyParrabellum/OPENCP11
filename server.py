import json, pdb
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime

CLUB_FILE = 'clubs.json'
COMP_FILE = 'competitions.json'
# If you want to set the current_time to now
CURRENT_TIME = datetime.now()
# If you want to set the current_time to before the competitions in the json file

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

competitions = loadCompetitions()
clubs = loadClubs()

def find_list_of_dict_index(list_of_dict, name):
    index = 0
    for dict in list_of_dict:
        if name in dict.values():
            return index
        index += 1

def load_and_rewrite_Competitions(comp_name, num_places):
    # Cette fonction prend en paramètre le lien vers le fichier json à utiliser pr
    # le test
    # Elle prend également en paramètres l'index de la competition à réecrire et le
    # nombre de places à booker
    # Ensuite elle enlève le nombre de places correspondantes
    with open("{}".format(COMP_FILE), "r") as jsonFile:
        data = json.load(jsonFile)

    comp_index = find_list_of_dict_index(competitions, comp_name)
    current_places = int(data['competitions'][comp_index]["numberOfPlaces"])

    data['competitions'][comp_index]["numberOfPlaces"] = str(current_places - num_places)

    with open("{}".format(COMP_FILE), "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

def load_and_rewrite_Clubs(club_name, points_to_deduct, place_value):
    # Cette fonction prend en paramètre le lien vers le fichier json à utiliser pr le
    # test
    # Elle prend également en paramètre l'index du club à réecrire et le nombre de 
    # places que le club aimerait booker
    # 1) On ouvre le fichier json en mode write
    # 2) on sélectionne l'endroit où il y a les points du club
    # 3) on déduit le bon nombre de points du club
    points_to_deduct = points_to_deduct * place_value
    with open("{}".format(CLUB_FILE), "r") as jsonFile:
        data = json.load(jsonFile)

    club_index = find_list_of_dict_index(clubs, club_name)
    current_points = int(data['clubs'][club_index]["points"])

    data['clubs'][club_index]["points"] = str(current_points - points_to_deduct)

    with open("{}".format(CLUB_FILE), "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


PLACE_VALUE = 1

app = Flask(__name__)
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
# @app.route('/showSummary',methods=['POST'])
# def showSummary():
#     club = [club for club in clubs if club['email'] == request.form['email']][0]
#     return render_template('welcome.html',club=club,competitions=competitions))


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


def can_purchase(club, competition, num_places, place_value, app_time=CURRENT_TIME):

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
    # Cette fonction pourrait aider la logique de la view purchase en tant que helper
    # Elle vérifie à partir de 2 paramètres, clubs et competitions, 
    # si un club a bien le bon nombre de points
    # pour purchase le nombre de places qu'il veut, si il reste toujours des places
    # dans la compétition, si le club peut prendre le bon nombre de places

@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    if request.form['optionnal_time']:
        CURRENT_TIME = request.form['optionnal_time']
    placesRequired = int(request.form['places'])
    if placesRequired > 12:
        flash("you can't book more than twelve places at once !")
        return render_template('welcome.html', club=club, competitions=competitions)
    if can_purchase(club, competition, placesRequired, PLACE_VALUE, CURRENT_TIME):
        load_and_rewrite_Clubs(club['name'], placesRequired, PLACE_VALUE)
        load_and_rewrite_Competitions(competition['name'], placesRequired)
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

if __name__ == "__main__":
    app.run(debug=True)
