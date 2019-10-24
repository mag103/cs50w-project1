import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
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

# KEY to Goodreads API
key = "QMP3DonwQHv1iCptVpVx8g"

# -----------------LOGIN-----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        if session.get('logged_in'):
            return redirect(url_for('home'))
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
        return redirect(url_for('home'))

# -----------------HOME PAGE-----------------

@app.route("/home", methods=["GET", "POST"])
def home():

    if request.method == "GET":

        if not session.get('logged_in'):
            return render_template("error.html", message="You need to log in to access this page.")

        username = db.execute("SELECT username FROM users WHERE id = :id", {"id": session['user_id']}).fetchall()[0]["username"]
        return render_template("home.html", username=username)

    if request.method == "POST":

        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")

        # Partly matching
        isbn = "%"+isbn+"%"
        title = "%"+title+"%"
        author = "%"+author+"%"

        # Check if there is at least one search result
        if db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author", {"isbn": isbn, "title": title, "author": author}).rowcount == 0:
            return render_template("error.html", message="There is no book that matches your search.")

        # Select all search results
        results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author", {"isbn": isbn, "title": title, "author": author}).fetchall()
        return render_template("search_results.html", results=results)


@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):

    if request.method == "GET":

        if not session.get('logged_in'):
            return render_template("error.html", message="You need to log in to access this page.")

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
        reviews_count = res.json()['books'][0]['reviews_count']
        average_rating = res.json()['books'][0]['average_rating']

        book_details = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

        user_id = session['user_id']
        username = db.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchall()[0]["username"]
        review_exist = 0

        if db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": isbn}).rowcount != 0:

            reviews = db.execute("SELECT users.id, username, rating, review_text FROM users INNER JOIN reviews ON reviews.user_id = users.id WHERE book_id = :book_id", {"book_id": isbn}).fetchall()

            for review in reviews:
                if username == review.username:
                    review_exist = review_exist + 1

            return render_template("book.html", book=book_details, reviews_count=reviews_count, average_rating=average_rating, reviews=reviews, username=username, review_exist=review_exist)

        return render_template("book.html", book=book_details, reviews_count=reviews_count, average_rating=average_rating, message="There are no reviews for this book yet.", username=username, review_exist=review_exist)

    if request.method == "POST":

        review_text = request.form.get("review_text")
        rating = request.form.get("rating")

        user_id = session['user_id']

        db.execute("INSERT INTO reviews (book_id, user_id, rating, review_text) VALUES (:book_id, :user_id, :rating, :review_text)",
                        {"book_id": isbn, "user_id": user_id, "rating": rating, "review_text": review_text})
        db.commit()

        return redirect(request.url)


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
            return render_template("error.html", title="Registration error", message="Username cannot be empty.")

        # Make sure password is not empty
        if not password:
            return render_template("error.html", title="Registration error", message="Password cannot be empty.")

        # Create username
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                        {"username": username, "password": password})
        db.commit()

        return render_template("registration_success.html", username=username, password=password)

# -----------------LOGOUT-----------------

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    return redirect(url_for('login'))

# -----------------API ACCESS-----------------
@app.route("/api/<isbn>")
def api(isbn):

    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        return render_template("error.html", title="Error 404", message="Book with this ISBN is not in the database.")

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    reviews_count = res.json()['books'][0]['reviews_count']
    average_rating = res.json()['books'][0]['average_rating']

    book_details = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    result = jsonify({
        "title": book_details.title,
        "author": book_details.author,
        "year": book_details.year,
        "isbn": book_details.isbn,
        "review_count": reviews_count,
        "average_score": average_rating
    })

    return result
