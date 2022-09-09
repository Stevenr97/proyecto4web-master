import os
import requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine("postgres://hsihffckvmhbcd:c80bdd334ef7782470866b6d5113e90221b7fecda9d45b18ca042a12d9d81edc@ec2-174-129-255-128.compute-1.amazonaws.com:5432/d20pndefq5jt86")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/shaders")
def shaders():
    return render_template("shaders.html")

@app.route("/rayT")
def rayT():
    return render_template("rayTracing.shapes.html")

@app.route("/registerattempt", methods=["POST"])

def registerattempt():


    reguser = request.form.get("reguser")
    regpass = request.form.get("regpass")
    regname = request.form.get("fname")

    if db.execute("SELECT * FROM users WHERE username = :user", {"user":reguser}).rowcount == 1:
        return render_template("error.html", message="Ese usuario ya existe")

    db.execute("INSERT INTO users (username, password, fullname) VALUES (:reguser, :regpass, :regname)", {"reguser": reguser, "regpass": regpass, "regname": regname})
    db.commit()
    return render_template("registersuccess.html", reguser=reguser)
@app.route("/extra")
def extra():
    return render_template("index.html")

@app.route("/login", methods=["POST"])

def login():


    try:
        user = request.form.get("user")
        password = request.form.get("password")
    except ValueError:
        return render_template("error.html"),404

    if db.execute("SELECT * FROM users where username= :user AND password = :pass",
                    {"user":user, "pass":password}).rowcount == 1:
        name = db.execute("SELECT fullname FROM users where username= :user AND password= :pass",
                        {"user":user, "pass":password}).fetchone()
        session["user"] = user

        return render_template("loginsuccess.html", fullname=name)
    else:
        return render_template("error.html", message="Usuario o Contraseña incorrecta")


@app.route("/logout", methods=["POST"])
def logout():

    session["user"] = None
    session["book-search"] = None
    session["book"] = None
    session["review"] = None
    session["average_rating"] = None
    session["total_count"] = None
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if session.get("user") is None:
        return render_template("login.html")
    return render_template("dashboard.html")

@app.route("/dashboardsearch", methods=["POST"])
def dashboardsearch():
    if session.get("user") is None:
        return render_template("login.html")
    search = request.form.get("book")
    helpsearch = '%' + search + '%'
    session["book-search"] = db.execute("SELECT * FROM books WHERE isbn LIKE :s1 or title LIKE :s2 or author LIKE :s3 or CAST(year as VARCHAR) LIKE :s4",
                                {"s1": helpsearch, "s2": helpsearch,"s3": helpsearch,"s4": helpsearch}).fetchall()
    if session["book-search"] is None:
        return render_template("dashboard.html", message="No book was found")
    else:
        return render_template("dashboard.html", books=session["book-search"])

@app.route("/bookdetails/<book_isbn>")
def bookdetails(book_isbn):
    if session.get("user") is None:
        return render_template("login.html")

    session["book"] = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if session["book"] is None:
        return render_template("dashboard.html", message = "Libro no econtrado")

    gr_key = "hDjwVUZn2RZm3t3fiyCqWQ"
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key":gr_key, "isbns":book_isbn})

    if res.status_code == 200:
        data = res.json()
        session["average_rating"] = data['books'][0]['average_rating']
        session["total_count"] = data['books'][0]['ratings_count']

    user = session.get("user")
    if res.status_code != 200:
        return render_template("books.html", book=session["book"], message2="No esta valorado en Goodreads", review=None)
    elif db.execute("SELECT * FROM reviews where isbn= :isbn AND username= :user",
                                {"isbn":book_isbn, "user":user}).rowcount == 0  :
        return render_template("books.html", book=session["book"], message="Libro sin calificar", review=None, average=session["average_rating"], total=session["total_count"])
    else:
        session["review"] = db.execute("SELECT rating, opinion FROM reviews where isbn= :isbn AND username= :user",
                                    {"isbn":book_isbn, "user":user}).fetchone() #try with session["user"]
        return render_template("books.html", book=session["book"], review=session["review"], average=session["average_rating"], total=session["total_count"])


@app.route("/reviewsubmission", methods=["POST"])
def reviewsubmission():

    if session.get("user") is None:
        return render_template("login.html")
    user = session.get("user")
    bookr = session.get("book")
    review = session.get("review")
    average_rating = session.get("average_rating")
    total_count = session.get("total_count")
    if db.execute("SELECT * FROM reviews WHERE isbn= :isbn AND username = :user",
                    {"isbn":bookr.isbn, "user":user}).rowcount == 1:
        return render_template("books.html",book=bookr, message="Este libro ya ha sido calificado", review=review)
    else:
        return render_template("review.html", book=bookr,average=average_rating, total=total_count)

@app.route("/review", methods=["POST"])
def reviewinsert():
    if session.get("user") is None:
        return render_template("login.html")
    user = session.get("user")
    book = session.get("book")
    opinion = request.form.get("opinion")
    rating = request.form.get("rating")
    average_rating = session.get("average_rating")
    total_count = session.get("total_count")
    submission = db.execute("INSERT INTO reviews VALUES (:isbn, :user, :opinion, :rating)",
                            {"isbn":book.isbn, "user":user, "opinion":opinion, "rating":rating})
    db.commit()
    session["review"] = db.execute("SELECT * FROM reviews where isbn= :isbn AND username= :user",
                                {"isbn":book.isbn, "user":user}).fetchone()
    return render_template("books.html", book=book, review=session["review"],average=average_rating, total=total_count)


@app.route("/bookdetails/api/<isbn>")
def book_api(isbn):
    if session.get("user") is None:
        return render_template("login.html")
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).rowcount == 0:
        return jsonify({"error": "Invalid isbn number"}), 404

    book = session.get("book")
    average_rating = session.get("average_rating")
    total_count = session.get("total_count")
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": total_count,
            "average_score": average_rating
        })
