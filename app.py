import os
from flask import Flask, render_template, redirect, request, session
#from flask_session import Session 
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

@app.route("/")
def index():
    return render_template("index.html")
if __name__ == "__main__":
    app.run()
