import os
import sqlite3
import datetime
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
    return render_template("index.html", recent_matches=recent_matches, fixes = fixes, ranks = ranks, results = results, player = player)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    player = featuredPlayer()
    # Forget any user_id
    #session.clear()
    dynamic_class = "hidden"
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            warn = "must provide username"
            return render_template("login.html", warn = warn)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password")

        # Query database for username
        res= db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        rows = res.fetchone()

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
                # Redirect user to home page
                check_persist = session.get("user_username")
                print(check_persist)
                recent_matches = display_recent_matches()
                fixes = fixtures()
                ranks = rank_teams()
                results = show_results()
                player = featuredPlayer()
                
                return render_template("index.html", recent_matches=recent_matches, fixes = fixes, ranks = ranks, results = results, rows = check_persist, dynamic_class = dynamic_class, player = player) 
            else:
                message = "User doesn't exist"
                dynamic_class = "visible"
                return render_template("login.html", message = message, dynamic_class = dynamic_class)   
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", dynamic_class = dynamic_class)

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
    session["name"] = None
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
        hash = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username or username in registeredUsers:
            return ("must provide username")
        elif not hash or hash != confirmation:
            return ("provided password did not match")
        else:
            db.execute("INSERT INTO 'users' (first_name, middle_name, last_name, username, hash) VALUES(?,?,?,?,?)", 
                       [first_name, middle_name, last_name, username, hash])
            con.commit()
            return render_template("register.html", registeredUsers = registeredUsers)
    return render_template("register.html")

@app.route("/teams")
def teams():
    # fetch data from the teams table
    db.execute("SELECT * FROM teams")
    teams = db.fetchall()
    return render_template("teams.html", teams=teams)

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
    # if not logged in , login first to add a match
    if request.method == "POST":
        # insert teams into the database
        # lookup the id for the teams and if not created insert it
        team_name = request.form.get("teamName") 
        county = request.form.get("county") 
        constituency = request.form.get("constituency")
        ward = request.form.get("ward")
        stadium = request.form.get("stadium")
        db.execute("SELECT name FROM teams WHERE name = ?", (team_name))
        team = db.fetchone()
        if team:
            myWarning = "team already exists"
            return myWarning
        else:
            db.execute("INSERT INTO 'teams' (name, county, constituency, ward, stadium) VALUES(?,?,?,?,?)",
                   [team_name, county, constituency, ward, stadium])
            con.commit()
        # display the dialog
    return render_template("teams.html", myWarning = myWarning)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8080)
