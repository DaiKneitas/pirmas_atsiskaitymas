import sqlite3
from models.book import Book
import uuid

def get_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # enable Foreign Key checks
    return conn

def db_add_book(db_path, book):
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO books (id, name, author, year, genre, copies)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(book.id), book.name, book.author, book.year, book.genre, book.copies)
        )

def db_get_all_books(db_path):
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, author, year, genre, copies FROM books")
        rows = cur.fetchall()

    books = []
    for (id_text, name, author, year, genre, copies) in rows:
        b = Book(name, author, year, genre, copies=copies)
        b.id = uuid.UUID(id_text)  # replace auto uuid with DB uuid
        books.append(b)
    return books