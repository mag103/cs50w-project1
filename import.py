import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create table "books" if it doesn't exist
if not engine.has_table("books"):
    db.execute("CREATE TABLE books (" +
                    "isbn VARCHAR PRIMARY KEY NOT NULL," +
                    "title VARCHAR NOT NULL," +
                    "author VARCHAR NOT NULL," +
                    "year VARCHAR NOT NULL" +
                    ")")
    db.commit()

# Read csv file
f = open("books.csv")
reader = csv.reader(f)
next(reader) # Skip first row (headers)

# Insert books from csv file into table
for isbn, title, author, year in reader: # loop gives each column a name
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0: # Check if book already exist in the table
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                  {"isbn": isbn, "title": title, "author": author, "year": year}) # substitute values from CSV line into SQL command, as per this dict
        # print(f"Added book isbn {isbn}, title {title}, author {author}, year {year}.")
    db.commit()
