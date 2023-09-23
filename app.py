import os
import sqlite3
import datetime
import base64
from flask import Flask, render_template, redirect, request, session
from flask_session import Session 
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)
# Configure session to use filesystem (instead of signed cookies)
SECRET_KEY = "changeme"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#conn = sqlite3.connect("derby.db", check_same_thread=False)
with sqlite3.connect("derby.db", check_same_thread=False) as con:
    db = con.cursor()
    if db:
        print("opened database successfully")
    else:
        print("Error opening the database")

# To check recently played matches
def display_recent_matches():
    # Calculate the date three days ago
    today = datetime.date.today()
    three_days_ago = today - datetime.timedelta(days=20)
    # Execute a SELECT query to fetch recent matches
    #db.execute("SELECT * FROM matches WHERE match_date >= ?", (three_days_ago,))
    db.execute("""
        SELECT matches.id, 
        teams.name AS home_team, 
        teams_away.name AS away_team, 
        matches.home_score,
        matches.away_score,
        matches.match_date 
        FROM matches 
        LEFT OUTER JOIN teams ON matches.home_team_id = teams.id 
        LEFT OUTER JOIN teams AS teams_away ON matches.away_team_id = teams_away.id 
        WHERE match_date >= ? LIMIT 3 """, (three_days_ago,))

    # Fetch all rows of data
    recent_matches = db.fetchall()

    return recent_matches

def display_teams(county,league):
    # fetch data from the teams
    teams = [] 
    if not county  and not league:
        db.execute("SELECT * FROM teams ORDER BY name ASC LIMIT 15")
        teams = db.fetchall()
    elif not county:
        db.execute("SELECT * FROM teams JOIN leagues ON teams.id = leagues.id_teams WHERE league = ?", (league,))
        teams = db.fetchall()
    else:
        db.execute("SELECT * FROM teams WHERE county = ? ORDER BY name ASC LIMIT 15", (county,))
        teams = db.fetchall()
    # convert the images into uri that can be rendered
    teams_with_data_uris = []
    for team in teams:
        team_id, team_name, logo_data,team_county, team_constituency, team_ward, team_stadium,  id_county = team

        if logo_data is None or logo_data.strip() == "":
            data_uri = "/static/logo/logo-dummy.png"
        else:
            logo_data_bytes = base64.b64decode(logo_data.encode('utf-8'))
            data_uri = f"data:image/png;base64,{base64.b64encode(logo_data_bytes).decode()}"
        teams_with_data_uris.append({"id": team_id, "name": team_name, "logo": data_uri, "county": team_county, "id_county": id_county, "constituency": team_constituency, "ward": team_ward, "stadium": team_stadium})
    return teams_with_data_uris
# To rank the teams in the standings table
def rank_teams():
    #check the registered teams
    db.execute("SELECT id FROM teams")
    teams_id = db.fetchall()

    # store team and its rank in a list as a dictionary
    ranking = []
    # iterate through the matches table to get the various ranking parameters
    # 1. Get matches played by each team
    for team in teams_id:
        db.execute("SELECT COUNT(*) AS total_matches FROM matches WHERE home_team_id = ? OR away_team_id = ?", (team[0], team[0]))
        matches_played = db.fetchone()
        ranking.append(matches_played)
    return ranking

def show_results():
    db.execute("""
         SELECT
            teams.name AS team_name,
            SUM(CASE WHEN matches.home_score > matches.away_score THEN 3
                     WHEN matches.home_score = matches.away_score THEN 1
                     ELSE 0 END) AS total_points,
            SUM(CASE WHEN matches.home_score > matches.away_score THEN 1
                     ELSE 0 END) AS total_wins,
            SUM(CASE WHEN matches.home_score = matches.away_score THEN 1
                     ELSE 0 END) AS total_draws,
            SUM(CASE WHEN matches.home_score < matches.away_score THEN 1
                     ELSE 0 END) AS total_losses
        FROM
            teams
        LEFT JOIN
            matches ON teams.id = matches.home_team_id OR teams.id = matches.away_team_id
        GROUP BY
            teams.name
        ORDER BY
            total_points DESC;


    """)

    results = db.fetchall()

    return results

#display upcoming matches
#show a pop up to ask if the user knows the results if it was never filled
# change past due games status from upcoming to postponed
# check if the game already in the recent matches
def fixtures():
    rows = db.execute("""
        SELECT 
        teams.name AS home_team, 
        teams_away.name AS away_team, 
        fixtures.match_date, 
        fixtures.match_time, 
        fixtures.venue 
        FROM fixtures 
        LEFT OUTER JOIN teams ON fixtures.home_team_id = teams.id 
        LEFT OUTER JOIN teams AS teams_away ON fixtures.away_team_id = teams_away.id
        """)
    upcoming = rows.fetchall()
    return upcoming
# display featured player of the day
def featuredPlayer():
    rows = db.execute("SELECT * FROM players WHERE id = 1")
    player = rows.fetchone()
    if player:
        return player
    else:
        return "Metasaka"

#session data as the user navigates around the page
def userSession():
 # Query database for username
    check_persist = session.get("user_username")
    return check_persist

# Render the landing page
@app.route("/")
def landingpage():
    recent_matches = display_recent_matches()
    upcoming = fixtures()
    games = []
    upcoming_games = []
    for match in recent_matches:
            games.append(match)
    for fix in upcoming:
            upcoming_games.append(fix)
        
    return render_template("landingpage.html", games = games, recent_matches=recent_matches, fixtures = upcoming_games)

@app.route("/index")
def index():
    recent_matches = display_recent_matches()
    fixes = fixtures()
    ranks = rank_teams()
    results = show_results()
    player = featuredPlayer()
    check_persist = userSession()
    return render_template("index.html", recent_matches=recent_matches, fixes = fixes, ranks = ranks, results = results, player = player, rows = check_persist)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    player = featuredPlayer()
    my_var = request.args.get('my_var', None)
    
    # Store my_var in the session
    session['my_var'] = my_var
    print(my_var)
    # Forget any user_id
    #session.clear()
    # dynamic class to hide the login option after a successiful login
    dynamic_class = "hidden"
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user_type = request.form.get('user_type', None)
        print(user_type)
        # Ensure username was submitted
        if not request.form.get("username"):
            warn = "must provide username"
            return render_template("index.html", player = player, warn = warn)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password")

        # Query database for username
        res= db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        rows = res.fetchone()
        res1= db.execute("SELECT type FROM types JOIN users ON users.id = types.id_users WHERE username = ?", [request.form.get("username")])
        usertype = res1.fetchall()

        # Ensure username exists and password is correct
        #if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        if not request.form.get("password"):
           return ("invalid username and/or password")
        
        else:
            # Remember which user has logged in
            
            if rows:
                session["user_id"] = rows[0]
                # set session username
                session["user_username"] = rows[1]
                # set session user type
                if len(usertype) == 2:
                    session["user_type1"] = usertype[0][0]
                    session["user_type2"] = usertype[1][0]
                else:
                    session["user_type1"] = usertype[0][0]
                
                # Style the page according to user type
                
                print(session.get("user_username"))
               # print(session["user_type2"])
                # Check if the keys exist in the session dictionary before accessing them
                
                if user_type == session.get("user_type1") or user_type == session.get("user_type2"):
                    # Redirect user to home page
                    recent_matches = display_recent_matches()
                    fixes = fixtures()
                    ranks = rank_teams()
                    results = show_results()
                    player = featuredPlayer()

                    # hide or show features based on user type
                    check_persist = session.get("user_username")
                    if user_type == 'sponsor':
                        user_id = 'sponsor'
                    elif user_type == 'normal':
                        user_id = 'normal' 
                    elif user_type == 'coach':
                        user_id = 'coach'                  
                    else:
                        user_id = 'player'
                    return render_template("index.html", recent_matches=recent_matches,user_id = user_id,
                                            fixes = fixes, data = rows[5], usertype = len(usertype), ranks = ranks, results = results,
                                              rows = check_persist, dynamic_class = dynamic_class, player = player, my_var = my_var) 
                return render_template("login.html",user_type = my_var)
            else:
                message = "User doesn't exist"
                dynamic_class = "visible"
                return render_template("index.html", message = message, player = player, dynamic_class = dynamic_class)   
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", dynamic_class = dynamic_class, player = player, my_var = my_var)

@app.route("/")
def index2():
  # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        print('no session data')
        return redirect("/login")
    return render_template('index.html')

@app.route("/logout")
def logout():
    session["user_username"] = None
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Query database for username
    registeredUsers = []
    users = db.execute("SELECT username FROM users")
    for user in users:
        registeredUsers.append(user[0])
    if request.method == "POST":

        first_name = request.form.get("firstname")
        middle_name = request.form.get("middlename")
        last_name = request.form.get("lastname")
        username = request.form.get("username")
        user_type = request.form.get("options")
        hash = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username or username in registeredUsers:
            return ("must provide username")
        elif not hash or hash != confirmation:
            return ("provided password did not match")
        else:
            db.execute("INSERT INTO 'users' (first_name, middle_name, last_name, username, hash, type) VALUES(?,?,?,?,?,?)", 
                       [first_name, middle_name, last_name, username, hash, user_type])
            con.commit()
            
            # start a session for the new user
            # Query database for username
            res= db.execute("SELECT * FROM users WHERE username = ?", [username])
            rows = res.fetchone()
            # set session ID and username 
            session["user_id"] = rows[0]
            session["user_username"] = username
            check_persist = session.get("user_username")
            return render_template("landingpage.html", rows = check_persist)
    return render_template("register.html")

@app.route("/teams")
def teams():
    teams = display_teams(0,0)
    db.execute("SELECT name FROM counties ORDER BY name")
    counties = db.fetchall()
    db.execute("SELECT DISTINCT(league) FROM leagues ORDER BY league")
    leagues = db.fetchall()
    check_persist = userSession()
    return render_template("teams.html", teams=teams, rows =  check_persist, counties = counties, leagues = leagues )

# add a recently played match
@app.route("/addMatch", methods=["GET", "POST"])
def add_match():
    # if not logged in , login first to add a match
    if request.method == "POST":
        # insert matches played into the database
        # lookup the id for the teams and if not created insert it

        homeTeam = request.form.get("home_team") 
        awayTeam = request.form.get("away_team")
        db.execute("SELECT id FROM teams WHERE name = ?", (homeTeam,))
        home = db.fetchone()
        print(home[0])
        print(f"Type home:{type(home[0])}")
        db.execute("SELECT id FROM teams WHERE name = ?", (awayTeam,))
        away = db.fetchone()
        matchDate = request.form.get("match_date") 
        matchTime = request.form.get("match_time")
        homeScore = request.form.get("home_score")
        awayScore = request.form.get("away_score")
        db.execute("INSERT INTO 'matches' (home_team_id, away_team_id, match_date, match_time, home_score, away_score) VALUES(?,?,?,?,?,?)",
                   [home[0], away[0], matchDate, matchTime, homeScore, awayScore])
        con.commit()
        # display the dialog
    return render_template("addMatch.html")
@app.route("/addTeam", methods=["GET", "POST"])
def add_team():
    # if not logged in , login first to add a team
    myWarning = "team already exists"
    teams = display_teams()
    db.execute("SELECT name FROM counties")
    counties = db.fetchone()
    if request.method == "POST":
        # insert teams into the database
        # lookup the id for the teams and if not created insert it
        team_name = request.form.get("teamName") 
        county = request.form.get("county") 

        # save the id of the county instead of the name
        db.execute("SELECT id FROM counties WHERE name = ?", [county])
        id_county = db.fetchone()
        id_county = id_county[0]

        constituency = request.form.get("constituency")
        ward = request.form.get("ward")
        stadium = request.form.get("stadium")
        logo = request.files["logo_image"]
        # Read binary data from the image file
        image_data = base64.b64encode(logo.read())
        image_data = image_data.decode('ascii')
        db.execute("SELECT name FROM teams WHERE name = ?", [team_name])
        team = db.fetchone()
        if team:
            return myWarning
        else:
            db.execute("INSERT INTO 'teams' (name, county, constituency, ward, stadium, logo, id_county) VALUES(?,?,?,?,?,?,?)",
                   [team_name, county, constituency, ward, stadium, image_data, id_county])
            con.commit()
        # display the dialog
    return render_template("teams.html", myWarning = myWarning, teams = teams, counties = counties)

# filter teams
@app.route("/filter", methods=["GET", "POST"])
def filter():
    db.execute("SELECT name FROM counties")
    counties = db.fetchone()
    teams = display_teams(0,0)
    
    if request.method == "POST":
        # get the specified county and league
        county = request.form.get('county')
        league = request.form.get('league')
        if county:
            teams = display_teams(county,league)
            print(county)
            return render_template("teams.html", teams = teams, counties = counties, applyFilter = "hidden", clearFilter = "visible" )
        else:
            return "No county name supplied"
    return render_template("teams.html", teams = teams, counties = counties)
    
# search for players and coaches biography
@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == "POST":
        requestedPlayer = request.form.get("search")
        if requestedPlayer:
            playerInfo = db.execute("SELECT * FROM players WHERE name = ?", [requestedPlayer])
            player = playerInfo.fetchone()
        else:
            return "No player name supplied"
    return render_template("player.html", player = player)

@app.route("/portfolio")
def portfolio():
    check_persist = session.get("user_username")
    print(check_persist)
    images_path = 'C:/Users/admin/Desktop/Heros-Derby/static/images'
    files = os.listdir(images_path)
    myfiles = []
    profile_photo = []
    digit = 2
    # populate the profile page with user photos
    for file in files:   
        if (check_persist + str(digit)) == file:
            myfiles.append(file)
            digit = digit + 1
    
    # set the profile photo
    for file in files:   
        if (check_persist + str(1)) == file:
            profile_photo.append(file)

    return render_template("portfolio.html", check_persist=check_persist, files = myfiles, profile_photo = profile_photo, rows = check_persist)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8080)
