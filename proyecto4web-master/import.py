import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://hsihffckvmhbcd:c80bdd334ef7782470866b6d5113e90221b7fecda9d45b18ca042a12d9d81edc@ec2-174-129-255-128.compute-1.amazonaws.com:5432/d20pndefq5jt86")

db = scoped_session(sessionmaker(bind=engine))

def main():
    file = open("books.csv")
    reader = csv.reader(file)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

if __name__ == "__main__":
    main()
