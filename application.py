import os

from flask import Flask, session, render_template, request, redirect, url_for
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
def welcome():
    return "Welcome. Placeholder for registration/login."

@app.route("/main_page", methods=["GET", "POST"])
def main_page():

    if request.method == "GET":

        if not session.get('logged_in'):
            return render_template("error.html", message="You need to log in to access this page.")

        username = db.execute("SELECT username FROM users WHERE id = :id", {"id": session['user_id']}).fetchall()[0]["username"]
        return render_template("main_page.html", username=username)

    if request.method == "POST":

        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")

        # Partly matching
        isbn = "%"+isbn+"%"
        title = "%"+title+"%"
        author = "%"+author+"%"

        # Check if there is at least one search result
        if db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": isbn}).rowcount == 0:
            return render_template("error.html", message="There is no book that matches your search.")

        # Select all search results
        results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": isbn}).fetchall()
        return render_template("search_results.html", results=results)

# -----------------REGISTRATION-----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Make sure if the username do not exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
            return render_template("error.html", message="User with this username already exists.")

        # Make sure username is not empty
        if not username:
            return render_template("error.html", message="Username cannot be empty.")

        # Make sure password is not empty
        if not password:
            return render_template("error.html", message="Password cannot be empty.")

        # Create username
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                        {"username": username, "password": password})
        db.commit()

        return render_template("hello.html", username=username, password=password)

# -----------------LOGIN-----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                        {"username": username, "password": password}).rowcount != 1:
            return render_template("error.html", message="Your credentials are incorrect. Please try again.")
        # Log in
        session['logged_in'] = True
        session['user_id'] = int(db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()[0]["id"])
        return redirect(url_for('main_page'))

# -----------------LOGOUT-----------------

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    return "You were just loged out."
