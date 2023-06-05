import os
import sqlite3

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

@app.route("/index")
def index():
    return render_template("index.html")
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


if __name__ == "__main__":
    app.run()
