import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgres://gdprrylxinxhyf:1c70b8250308bf89bf1898c1bbb82189816ee70af5c57bf06a4cfab31c12489a@ec2-18-206-84-251.compute-1.amazonaws.com:5432/dfo5s0a7s22gr8')

db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year, review_count, avg) VALUES (:isbn, :title, :author, :year, 0, 0)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book title {title} by {author} in {year} .")
    db.commit()

if __name__ == "__main__":
    main()
