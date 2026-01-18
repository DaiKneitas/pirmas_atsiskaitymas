import datetime as dt
import random
from models.book import Book
from models.reader import Reader
from models.librarian import Librarian
from models.loan import Loan
from config import MAX_BOOKS_PER_READER, DEFAULT_LOAN_DAYS


class Library:
    def __init__(self):
        self.books = {}                 
        self.loans = []
        self.readers = {}               
        self.librarians = {}
        self.starter_pack_added = False
        self.current_date = dt.datetime.now()

        # statistikai
        self.borrowed_genre_counts = {}



    # ----- Registracija / auth -----
    def add_librarian(self, user_name, password):
        user_name = user_name.strip()
        password = password.strip()

        if not user_name or not password:
            raise ValueError("☠️❌ Vardas ir slaptažodis negali būti tušti.")
        if user_name in self.librarians:
            raise ValueError("☠️❌ Toks bibliotekininkas jau egzistuoja.")

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
            raise ValueError("☠️❌ Vardas, pavardė ir slaptažodis negali būti tušti.")

        card_id = self._generate_reader_card_id(name, last_name)
        reader = Reader(name, last_name, card_id, password)
        self.readers[card_id] = reader
        return reader
    

    def authenticate_reader(self, card_id, password):
        reader = self.readers.get(card_id)
        if reader and reader.password == password:
            return reader
        return None



    # ----- Library services -----
    def add_book(self, name, author, year, genre, copies=1):
        name = name.strip()
        author = author.strip()
        genre = genre.strip()

        if not name or not author or not genre:
            raise ValueError("☠️❌ Pavadinimas, autorius ir žanras negali būti tušti.")

        if year < -1000 or year > 2100:
            raise ValueError("☠️❌ Neteisingi išleidimo metai.")

        if copies < 1:
            raise ValueError("☠️❌ Kopijų skaičius turi būti bent 1.")
        
        name_check = name.lower()
        author_check = author.lower()
        for libr_book in self.books.values():
            if libr_book.name.lower() == name_check and libr_book.author.lower() == author_check and libr_book.year == year:
                libr_book.copies += copies
                return libr_book

        book = Book(name, author, year, genre, copies=copies)
        self.books[book.id] = book
        return book


    def list_all_books(self):
        return list(self.books.values())
    

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
    

    def list_available_books(self):
        available = []
        for book_id, book in self.books.items():
            if self.available_copies(book_id) > 0:
                available.append(book)
        return available


    def delete_old_books(self, oldest_possible_year):
        to_delete = []
        for book_id, book in self.books.items():
            has_no_loans = self.borrowed_copies_count(book_id) == 0
            if book.year < oldest_possible_year and has_no_loans:
                to_delete.append(book_id)

        for book_id in to_delete:
            del self.books[book_id]

        return len(to_delete)
    


    # ----- metodai datos pakeitimui -----
    def now(self):
        return self.current_date


    def set_current_date(self, year, month, day):
        self.current_date = dt.datetime(year, month, day)



    # ----- metodai knygų išdavimui / gražinimui ir negražintų knygų patikrai -----
    def reader_has_overdue(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        for loan in self.loans:
            if loan.reader_card_id == reader_card_id and loan.return_date < now:
                return True

        return False
    

    def list_overdue_loans(self, now=None):
        if now is None:
            now = self.now()

        overdue = []
        for loan in self.loans:
            if loan.return_date < now:
                overdue.append(loan)
        return overdue


    def overdue_count_for_reader_meniu(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        count = 0
        for loan in self.loans:
            if loan.reader_card_id == reader_card_id and loan.return_date < now:
                count += 1
        return count


    def find_loan(self, reader_card_id, book_id):
        for loan in self.loans:
            if loan.reader_card_id == reader_card_id and loan.book_id == book_id:
                return loan
        return None


    def lend_book(self, reader_card_id, book_id, days=DEFAULT_LOAN_DAYS, max_books=MAX_BOOKS_PER_READER):
        if reader_card_id not in self.readers:
            raise ValueError("☠️❌ Nerastas skaitytojas su tokiu kortelės numeriu.")
        if book_id not in self.books:
            raise ValueError("☠️❌ Nerasta tokia knyga.")
        if days <= 0:
            raise ValueError("☠️❌ Dienų skaičius turi būti teigiamas.")

        reader = self.readers[reader_card_id]

        if len(reader.taken_book_ids) >= max_books:
            raise ValueError(f"☠️❌ Pasiektas paimtų knygų limitas. Galima pasiimti tik {max_books} knygas")

        if self.reader_has_overdue(reader_card_id):
            raise ValueError("☠️❌ Negalima pasiimti knygos: turite vėluojančią knygą!")

        if self.available_copies(book_id) <= 0:
            raise ValueError("☠️❌ Šiuo metu nėra laisvų šios knygos kopijų.")

        borrow_date = self.now()
        return_date = borrow_date + dt.timedelta(days=days)

        new_loan = Loan(book_id, reader_card_id, borrow_date, return_date)
        self.loans.append(new_loan)

        reader.taken_book_ids.append(book_id)

        # statistikai
        genre = self.books[book_id].genre
        if genre in self.borrowed_genre_counts:
            self.borrowed_genre_counts[genre] += 1
        else:
            self.borrowed_genre_counts[genre] = 1

        return new_loan


    def return_book(self, reader_card_id, book_id):
        if reader_card_id not in self.readers:
            raise ValueError("☠️❌ Nerastas skaitytojas su tokiu kortelės numeriu.")

        loan_index = None
        for i, loan in enumerate(self.loans):
            if loan.reader_card_id == reader_card_id and loan.book_id == book_id:
                loan_index = i
                break

        if loan_index is None:
            raise ValueError("☠️❌ Šis skaitytojas nėra paėmęs šios knygos.")

        del self.loans[loan_index]

        reader = self.readers[reader_card_id]
        if book_id in reader.taken_book_ids:
            reader.taken_book_ids.remove(book_id)

    


    # ----- Library statistics -----
    def statistics(self, now=None):
        if now is None:
            now = self.now()

        total_books = len(self.books)

        total_copies = 0
        for book in self.books.values():
            total_copies += book.copies

        total_loans = len(self.loans)
        overdue_loans = self.list_overdue_loans(now)
        overdue_count = len(overdue_loans)

        # average overdue days
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
            "total_copies": total_copies,
            "total_loans": total_loans,
            "overdue_count": overdue_count,
            "avg_overdue_days": avg_overdue_days,
            "most_common_genre": most_common_genre,
            "most_borrowed_genre": most_borrowed_genre,
        }