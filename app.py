import os
import requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not ("postgres://gdprrylxinxhyf:1c70b8250308bf89bf1898c1bbb82189816ee70af5c57bf06a4cfab31c12489a@ec2-18-206-84-251.compute-1.amazonaws.com:5432/dfo5s0a7s22gr8"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('postgres://gdprrylxinxhyf:1c70b8250308bf89bf1898c1bbb82189816ee70af5c57bf06a4cfab31c12489a@ec2-18-206-84-251.compute-1.amazonaws.com:5432/dfo5s0a7s22gr8')
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"

@app.route("/login", methods=["GET", "POST"])
def login():
    print(session)
    if session.get('username') != None:
        return render_template("home.html")
    return render_template("login.html", check=0, check2=0)

@app.route("/authenticate", methods=["POST"])
def authenticate():
    name = request.form.get("name")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": name}).rowcount != 0:
        if db.execute("SELECT * FROM users WHERE username = :username AND PASSWORD = :password", {"username": name, "password":password}).rowcount == 0:
            return render_template("login.html", check=1, check2=0)
        else:
            session['username'] =  name
            return render_template("home.html", name=name)
    else:
        return render_template("login.html", check=0, check2=1)

@app.route("/register", methods=["POST"])
def register():
    return render_template("register.html") 

@app.route("/success", methods=["POST"])
def success():
    name = request.form.get("name")
    password = request.form.get("password")
    db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
    {"username": name, "password":password})
    db.commit();
    return render_template("error.html", error="Registered")


@app.route("/search", methods=["POST"])
def search():
    title = '%' + request.form.get("title") + '%'
    author = '%' + request.form.get("author") + '%'
    isbn = '%' +  request.form.get("isbn") + '%'

    books = db.execute("SELECT * FROM books WHERE title ILIKE :title AND author ILIKE :author AND isbn ILIKE :isbn", {"title": title, "author": author, "isbn": isbn})
    return render_template("books.html", books=books)


@app.route("/searchshow", methods=["GET", "POST"])
def searchshow():
    return render_template("search.html")

@app.route("/logout")
def logout():
   
    return render_template("login.html", check = 0, check2 = 0)


@app.route("/books/<string:isbn_val>", methods=["GET", "POST"])
def book(isbn_val):
    """ """
    check = 0
    review_user = db.execute("SELECT * FROM reviews WHERE isbn=:isbn AND username=:username", {"isbn": isbn_val, "username": session['username']}).fetchall()
    if review_user != []:
        check = 1
    
    if request.method == "POST":
       print(check)
       if check == 0: 
            review = request.form.get("review")
            db.execute("INSERT INTO reviews(isbn, review, username) VALUES (:isbn, :review, :username)", {"isbn": isbn_val, "review": review, "username": session['username']})
            db.execute("UPDATE books SET review_count = review_count + 1 WHERE isbn = :isbn", {"isbn": isbn_val })
            db.commit()
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn_val}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn": isbn_val}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "d15JSGZZ0mrH1cWlwOBLcg", "isbns": [book.isbn], "format": "json"})
    ##print(res)
    data = res.json()
    ##print(data["books"][0]["work_reviews_count"])
    ##print(data["books"][0]["average_rating"])
    goodreads_date = {data["books"][0]["work_reviews_count"], data["books"][0]["average_rating"]}
    return render_template("book.html", book=book, reviews=reviews, check=check, goodreads_data=goodreads_date)


@app.route("/api/books/<string:isbn_val>")
def mybook_api(isbn_val):
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn_val}).fetchone()
    print(book)
    if book == None:
        return jsonify({
            "error": "Book not found"
        })
    else:
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": book.review_count
        })
