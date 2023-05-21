import os
import sqlite3

from flask import Flask, render_template, redirect, request, session
#from flask_session import Session 
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Configure CS50 Library to use SQLite database
db = sqlite3.connect("derby.db")

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return ("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # set session username
        session["user_username"] = rows[0]["username"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
if __name__ == "__main__":
    app.run()
