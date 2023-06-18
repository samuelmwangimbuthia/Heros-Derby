import os
import sqlite3
import datetime
from flask import Flask, render_template, redirect, request, session
from flask_session import Session 
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

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
    three_days_ago = today - datetime.timedelta(days=100)
    # Execute a SELECT query to fetch recent matches
    #db.execute("SELECT * FROM matches WHERE match_date >= ?", (three_days_ago,))
    db.execute("SELECT matches.id, teams.name AS home_team, teams_away.name AS away_team, matches.home_score,matches.away_score,matches.match_date FROM matches LEFT OUTER JOIN teams ON matches.home_team_id = teams.id LEFT OUTER JOIN teams AS teams_away ON matches.away_team_id = teams_away.id WHERE match_date >= ?", (three_days_ago,))

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
    results = []
    # iterate through the matches table to get the various ranking parameters
    for team in teams_id:
        db.execute("SELECT COUNT(*) AS total_matches FROM matches WHERE home_team_id = ? OR away_team_id = ?", team, team)
        matches_played = db.fetchone()
        ranking.append( matches_played)
    
    # check the result for each team
    for team in teams_id:
        db.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? AND home_score > away_score OR away_score > home_score", team)
        win = db.fetchone()
        db.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? AND home_score = away_score", team )
        draw = db.fetchone()
        # compute point gunnered in each match
        points = 0
        if win:
            points += 3
        elif draw:
            points += 1
        else:
            points = 0
    
#display upcoming matches
#show a pop up to ask if the user knows the results if it was never filled
# change past due games status from upcoming to postponed
# check if the game already in the recent matches
@app.route("/index")
def index():
    recent_matches = display_recent_matches()
    return render_template("index.html", recent_matches=recent_matches)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    #session.clear()

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
            session["user_id"] = rows[0]
            # set session username
            session["user_username"] = rows[1]
            # Redirect user to home page
            check_persist = session.get("user_username")
            print(check_persist)
            return render_template("index.html", rows = check_persist)    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

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
        db.execute("SELECT id FROM teams WHERE name = ?", (awayTeam,))
        away = db.fetchone()
        matchDate = request.form.get("match_date") 
        matchTime = request.form.get("match_time")
        homeScore = request.form.get("home_score")
        awayScore = request.form.get("away_score")
        db.execute("INSERT INTO 'matches' (home_team_id, away_team_id, match_date, match_time, home_score, away_score) VALUES(?,?,?,?,?,?)",
                   [home[0], away[0], matchDate, matchTime, homeScore, awayScore])
        con.commit()
    return render_template("addMatch.html")

if __name__ == "__main__":
    app.run()
