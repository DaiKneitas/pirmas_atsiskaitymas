# library.py

import datetime as dt
from uuid import UUID
import random
from models.book import Book
from models.reader import Reader
from models.librarian import Librarian


class Loan:
    def __init__(self, book_id, reader_card_id, borrowed_at, due_at):
        self.book_id = book_id
        self.reader_card_id = reader_card_id
        self.borrowed_at = borrowed_at
        self.due_at = due_at


class Library:
    def __init__(self):
        self.books = {}                 
        self.loans = []
        self.readers = {}               
        self.librarians = {}
        # statistikai
        self.borrowed_genre_counts = {}

    # ----- Registracija / auth -----

    def add_librarian(self, user_name, password):
        user_name = user_name.strip()
        password = password.strip()

        if not user_name or not password:
            raise ValueError("Vardas ir slaptažodis negali būti tušti.")
        if user_name in self.librarians:
            raise ValueError("Toks bibliotekininkas jau egzistuoja.")

        libr = Librarian(user_name, password)
        self.librarians[user_name] = libr
        return libr
    

    def authenticate_librarian(self, user_name, password):
        libr = self.librarians.get(user_name)
        if libr and libr.password == password:
            return libr
        return None
    

    def _generate_reader_card_id(self, name, last_name):
        initials = (name[:1] + last_name[:1]).upper()
        while True:
            digits = str(random.randint(0, 999999)).zfill(6)
            card_id = f"{initials}-{digits}"
            if card_id not in self.readers:
                return card_id
    
    
    def register_reader(self, name, last_name, password):
        name = name.strip()
        last_name = last_name.strip()
        password = password.strip()

        if not name or not last_name or not password:
            raise ValueError("Vardas, pavardė ir slaptažodis negali būti tušti.")

        card_id = self._generate_reader_card_id(name, last_name)
        reader = Reader(name, last_name, card_id, password)
        self.readers[card_id] = reader
        return reader
    

    def authenticate_reader(self, card_id, password):
        reader = self.readers.get(card_id)
        if reader and reader.password == password:
            return reader
        return None

           
    def add_book(self, name, author, year, genre, copies=1):
        name = name.strip()
        author = author.strip()
        genre = genre.strip()

        if not name or not author or not genre:
            raise ValueError("Pavadinimas, autorius ir žanras negali būti tušti.")

        current_year = dt.datetime.now().year
        if year < 0 or year > current_year + 1:
            raise ValueError("Neteisingi išleidimo metai.")

        if copies < 1:
            raise ValueError("Kopijų skaičius turi būti bent 1.")

        book = Book(name, author, year, genre, copies=copies)
        self.books[book.id] = book
        return book


    def list_all_books(self):
        return list(self.books.values())