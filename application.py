import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"

@app.route("/register", methods=["GET"])
def register():

    return render_template("register.html")

@app.route("/register", methods=["POST"])
def hello():
    username = request.form.get("username") # take the request the user made, access the form,
                                    # and store the field called `name` in a Python variable also called `name`
    password = request.form.get("password")

    # if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:

    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, "password": password})
    db.commit()

    return render_template("hello.html", username=username, password=password)