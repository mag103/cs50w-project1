# Project 1: Books

This website was created for the purpose of Project 1 of Harvard's course CS50's Web Programming with Python and JavaScript.

### Objectives
* Become more comfortable with Python.
* Gain experience with Flask.
* Learn to use SQL to interact with databases.

### Overview
In this project, I've built a book review website. Users are be able to register for my website and then log in using their username and password. Once they log in, they are able to search for books, leave reviews for individual books, and see the reviews made by other users. Additionaly a third-party API by Goodreads was used to pull in ratings from a broader audience. Users are also able to query for book details and book reviews programmatically via my website’s API.

### What was used for this project?
* PostgreSQL database (hosted by Heroku, an online web hosting service)
  * Table "users" - containing information about registered users
  * Table "books" - containing details of 5000 books
  * Table "reviews" - containing users' book reviews and ratings
 * Python and Flask
 * Goodreads API
 
### What's contained in each file?
* application.py - web application Python file, using Flask and SQLAlchemy to navigate between routes, html pages, exectute SQL commands, control sessions etc.
* import.py - Python program that takes the books from CSV file and imports them into PostgreSQL database
* folder templates - contains .html files:
  * layout - file containg page layout that is used across all other html files
  * login - page with the login form
  * register - page with the register form
  * registration_success - page with successful registration confirmation
  * home - page with the search form - allows user to search book by it's ISBN, Author or Title
  * search_results - page with a table containg search results
  * book - page containg book details, Goodreads average rating and number of ratings, review form and list of all users' reviews
  * error - page displaying error message, for example if there is no search results to display or if user enters incorrect credentials while trying to log in
* folder static - containg stylesheet and scss mapping:
  * styles.css
  * styles.scss
  * styles.css.map
* books.csv - file with book details (imported by import.py to PostgreSQL database)
* requirements.txt - file listing all Python packages that need to be installed in order to run the web application
