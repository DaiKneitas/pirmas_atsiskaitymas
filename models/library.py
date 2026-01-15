# library.py

import datetime as dt
from uuid import UUID
import random
from models.book import Book
from models.reader import Reader
from models.librarian import Librarian


class Loan:
    def __init__(self, book_id, reader_card_id, borrow_date, return_date):
        self.book_id = book_id
        self.reader_card_id = reader_card_id
        self.borrow_date = borrow_date
        self.return_date = return_date


class Library:
    def __init__(self):
        self.books = {}                 
        self.loans = []
        self.readers = {}               
        self.librarians = {}
        self.starter_pack_added = False
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
        if year < -5000 or year > current_year + 1:
            raise ValueError("Neteisingi išleidimo metai.")

        if copies < 1:
            raise ValueError("Kopijų skaičius turi būti bent 1.")

        book = Book(name, author, year, genre, copies=copies)
        self.books[book.id] = book
        return book


    def list_all_books(self):
        return list(self.books.values())
    

    def list_available_books(self):
        available = []
        for book_id, book in self.books.items():
            if book_id not in self.loans:
                available.append(book)
        return available
    

    def search_books(self, text):
        text = text.strip().lower()
        found_books = []

        if text == "":
            return []

        for book in self.books.values():
            title = book.name.lower()
            author = book.author.lower()

            if text in title or text in author:
                found_books.append(book)

        return found_books
    

    def borrowed_copies_count(self, book_id):
        count = 0
        for loan in self.loans:
            if loan.book_id == book_id:
                count += 1
        return count
    

    def available_copies(self, book_id):
        book = self.books.get(book_id)
        if not book:
            return 0
        borrowed = self.borrowed_copies_count(book_id)
        return book.copies - borrowed


    def delete_old_books(self, oldest_possible_year):
        to_delete = []
        for book_id, book in self.books.items():
            has_no_loans = self.borrowed_copies_count(book_id) == 0
            if book.year < oldest_possible_year and has_no_loans:
                to_delete.append(book_id)

        for book_id in to_delete:
            del self.books[book_id]

        return len(to_delete)
    

    def reader_has_overdue(self, reader_card_id, now=None):
        if now is None:
            now = dt.datetime.now()

        for loan in self.loans:  # loans is a list
            if loan.reader_card_id == reader_card_id and loan.return_date < now:
                return True

        return False
    

    def list_overdue_loans(self, now=None):
        now = now or dt.datetime.now()
        overdue = []
        for loan in self.loans:
            if loan.return_date < now:
                overdue.append(loan)
        return overdue
    

    def statistics(self, now=None):
        if now is None:
            now = dt.datetime.now()

        total_books = len(self.books)
        total_loans = len(self.loans)

        overdue_loans = self.list_overdue_loans(now)
        overdue_count = len(overdue_loans)

        # average overdue days (only for overdue loans)
        overdue_days_sum = 0
        for loan in overdue_loans:
            overdue_days_sum += (now - loan.return_date).days

        if overdue_count == 0:
            avg_overdue_days = 0
        else:
            avg_overdue_days = overdue_days_sum / overdue_count

        # most common genre in library
        genre_counts = {}
        for book in self.books.values():
            genre = book.genre
            if genre in genre_counts:
                genre_counts[genre] += 1
            else:
                genre_counts[genre] = 1

        if len(genre_counts) == 0:
            most_common_genre = None
        else:
            most_common_genre = max(genre_counts, key=genre_counts.get)

        # most borrowed genre
        if len(self.borrowed_genre_counts) == 0:
            most_borrowed_genre = None
        else:
            most_borrowed_genre = max(self.borrowed_genre_counts, key=self.borrowed_genre_counts.get)

        return {
            "total_books": total_books,
            "total_loans": total_loans,
            "overdue_count": overdue_count,
            "avg_overdue_days": avg_overdue_days,
            "most_common_genre": most_common_genre,
            "most_borrowed_genre": most_borrowed_genre,
        }