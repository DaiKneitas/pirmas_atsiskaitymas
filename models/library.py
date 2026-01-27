import sqlite3
import uuid
import datetime as dt
import random

from models.book import Book
from models.reader import Reader
from models.librarian import Librarian
from models.loan import Loan
from config import MAX_BOOKS_PER_READER, DEFAULT_LOAN_DAYS


class Library:
    def __init__(self, db_path):
        self.db_path = db_path
        self.starter_pack_added = False
        self.current_date = dt.datetime.now()

        # statistikai
        self.borrowed_genre_counts = {}



    # ---------- DB helpers ----------
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _dt_to_text(self, date):
        return date.isoformat(timespec="seconds")

    def _text_to_dt(self, seconds):
        return dt.datetime.fromisoformat(seconds)
    

    # ----- metodai datos pakeitimui -----
    def now(self):
        return self.current_date


    def set_current_date(self, year, month, day):
        self.current_date = dt.datetime(year, month, day)


    # ----- Registracija / auth -----
    def add_librarian(self, user_name, password):
        user_name = user_name.strip()
        password = password.strip()

        if not user_name or not password:
            raise ValueError("☠️❌ Vardas ir slaptažodis negali būti tušti.")

        try:
            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO librarians (user_name, password) VALUES (?, ?)",
                    (user_name, password),
                )
        except sqlite3.IntegrityError:
            # user_name PRIMARY KEY already exists
            raise ValueError("☠️❌ Toks bibliotekininkas jau egzistuoja.")

        return Librarian(user_name, password)
    

    def authenticate_librarian(self, user_name, password):
        user_name = user_name.strip()
        password = password.strip()

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_name, password FROM librarians WHERE user_name = ?",
                (user_name,),
            )
            row = cur.fetchone()

        if not row:
            return None

        db_user, db_pass = row
        if db_pass == password:
            return Librarian(db_user, db_pass)
        return None
    

    def _generate_reader_card_id(self, name, last_name):
        initials = (name[:1] + last_name[:1]).upper()

        while True:
            digits = str(random.randint(0, 999999)).zfill(6)
            card_id = f"{initials}-{digits}"

            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM readers WHERE card_id = ?", (card_id,))
                if not cur.fetchone():
                    return card_id
    
    
    def register_reader(self, name, last_name, password):
        name = name.strip()
        last_name = last_name.strip()
        password = password.strip()

        if not name or not last_name or not password:
            raise ValueError("☠️❌ Vardas, pavardė ir slaptažodis negali būti tušti.")

        card_id = self._generate_reader_card_id(name, last_name)

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO readers (card_id, name, last_name, password) VALUES (?, ?, ?, ?)",
                (card_id, name, last_name, password),
            )

        r = Reader(name, last_name, card_id, password)
        r.taken_book_ids = self._get_taken_book_ids(card_id)
        return r
    

    def authenticate_reader(self, card_id, password):
        card_id = card_id.strip()
        password = password.strip()

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT card_id, name, last_name, password FROM readers WHERE card_id = ?",
                (card_id,),
            )
            row = cur.fetchone()

        if not row:
            return None

        db_card, name, last_name, db_pass = row
        if db_pass != password:
            return None

        r = Reader(name, last_name, db_card, db_pass)
        r.taken_book_ids = self._get_taken_book_ids(db_card)
        return r



    # ----- Library services -----

    def get_book_by_id(self, book_id):
        """
        Returns Book object by UUID (or UUID text). If not found -> None
        """
        book_id_text = str(book_id)

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, author, year, genre, copies FROM books WHERE id = ?",
                (book_id_text,),
            )
            row = cur.fetchone()

        if not row:
            return None

        book_id_text, name, author, year, genre, copies = row
        b = Book(name, author, year, genre, copies=copies)
        b.id = uuid.UUID(book_id_text)
        return b



    def _get_taken_book_ids(self, reader_card_id):
        # active loans only
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT book_id
                FROM loans
                WHERE reader_card_id = ? AND returned_at IS NULL
                """,
                (reader_card_id,),
            )
            rows = cur.fetchall()

        ids = []
        for (book_id_text,) in rows:
            ids.append(uuid.UUID(book_id_text))
        return ids



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

        with self._get_conn() as conn:
            cur = conn.cursor()

            # find same book, add copies to it
            cur.execute(
                """
                SELECT id, name, author, year, genre, copies
                FROM books
                WHERE lower(name)=? AND lower(author)=? AND year=?
                """,
                (name_check, author_check, year),
            )
            row = cur.fetchone()

            if row:
                book_id_text, db_name, db_author, db_year, db_genre, db_copies = row
                new_copies = db_copies + copies
                cur.execute("UPDATE books SET copies = ? WHERE id = ?", (new_copies, book_id_text))

                b = Book(db_name, db_author, db_year, db_genre, copies=new_copies)
                b.id = uuid.UUID(book_id_text)
                return b

            # insert new book
            book_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO books (id, name, author, year, genre, copies)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (book_id, name, author, year, genre, copies),
            )

        b = Book(name, author, year, genre, copies=copies)
        b.id = uuid.UUID(book_id)
        return b


    def list_all_books(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, author, year, genre, copies FROM books ORDER BY name")
            rows = cur.fetchall()

        books = []
        for book_id_text, name, author, year, genre, copies in rows:
            b = Book(name, author, year, genre, copies=copies)
            b.id = uuid.UUID(book_id_text)
            books.append(b)
        return books
    

    def search_books(self, text):
        text = text.strip().lower()
        if text == "":
            return []

        like = f"%{text}%"
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, author, year, genre, copies
                FROM books
                WHERE lower(name) LIKE ? OR lower(author) LIKE ?
                ORDER BY name
                """,
                (like, like),
            )
            rows = cur.fetchall()

        books = []
        for book_id_text, name, author, year, genre, copies in rows:
            b = Book(name, author, year, genre, copies=copies)
            b.id = uuid.UUID(book_id_text)
            books.append(b)
        return books
    


    # ---------- Copies / availability ----------
    def borrowed_copies_count(self, book_id):
        book_id_text = str(book_id)
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT COUNT(*)
                FROM loans
                WHERE book_id = ? AND returned_at IS NULL
                """,
                (book_id_text,),
            )
            return cur.fetchone()[0]
    

    def available_copies(self, book_id):
        book_id_text = str(book_id)

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT copies FROM books WHERE id = ?", (book_id_text,))
            row = cur.fetchone()

        if not row:
            return 0

        total_copies = row[0]
        borrowed = self.borrowed_copies_count(book_id)
        return total_copies - borrowed
    

    def list_available_books(self):
        books = self.list_all_books()
        available = []
        for b in books:
            if self.available_copies(b.id) > 0:
                available.append(b)
        return available


    def delete_old_books(self, oldest_possible_year):
        # delete only if no active loans for book_id
        deleted = 0

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, year FROM books")
            rows = cur.fetchall()

            for book_id_text, year in rows:
                if year >= oldest_possible_year:
                    continue

                cur.execute(
                    "SELECT COUNT(*) FROM loans WHERE book_id = ? AND returned_at IS NULL",
                    (book_id_text,),
                )
                active = cur.fetchone()[0]
                if active == 0:
                    cur.execute("DELETE FROM books WHERE id = ?", (book_id_text,))
                    deleted += 1

        return deleted
    


    # ----- metodai knygų išdavimui / gražinimui ir negražintų knygų patikrai -----
    def reader_has_overdue(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        now_text = self._dt_to_text(now)

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 1
                FROM loans
                WHERE reader_card_id = ?
                  AND returned_at IS NULL
                  AND return_date < ?
                LIMIT 1
                """,
                (reader_card_id, now_text),
            )
            return cur.fetchone() is not None
    

    def list_overdue_loans(self, now=None):
        if now is None:
            now = self.now()

        now_text = self._dt_to_text(now)

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT book_id, reader_card_id, borrow_date, return_date
                FROM loans
                WHERE returned_at IS NULL AND return_date < ?
                ORDER BY return_date
                """,
                (now_text,),
            )
            rows = cur.fetchall()

        loans = []
        for book_id_text, reader_card_id, borrow_text, return_text in rows:
            loan = Loan(
                uuid.UUID(book_id_text),
                reader_card_id,
                self._text_to_dt(borrow_text),
                self._text_to_dt(return_text),
            )
            loans.append(loan)
        return loans


    def overdue_count_for_reader_meniu(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        now_text = self._dt_to_text(now)

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT COUNT(*)
                FROM loans
                WHERE reader_card_id = ?
                  AND returned_at IS NULL
                  AND return_date < ?
                """,
                (reader_card_id, now_text),
            )
            return cur.fetchone()[0]


    def find_loan(self, reader_card_id, book_id):
        # active loan only
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT borrow_date, return_date
                FROM loans
                WHERE reader_card_id = ? AND book_id = ? AND returned_at IS NULL
                """,
                (reader_card_id, str(book_id)),
            )
            row = cur.fetchone()

        if not row:
            return None

        borrow_text, return_text = row
        return Loan(book_id, reader_card_id, self._text_to_dt(borrow_text), self._text_to_dt(return_text))



    def lend_book(self, reader_card_id, book_id, days=DEFAULT_LOAN_DAYS, max_books=MAX_BOOKS_PER_READER):
 
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM readers WHERE card_id = ?", (reader_card_id,))
            if not cur.fetchone():
                raise ValueError("☠️❌ Nerastas skaitytojas su tokiu kortelės numeriu.")


            cur.execute("SELECT copies, genre FROM books WHERE id = ?", (str(book_id),))
            book_row = cur.fetchone()
            if not book_row:
                raise ValueError("☠️❌ Nerasta tokia knyga.")

            if days <= 0:
                raise ValueError("☠️❌ Dienų skaičius turi būti teigiamas.")

            # if max books limit reached
            cur.execute(
                """
                SELECT COUNT(*)
                FROM loans
                WHERE reader_card_id = ? AND returned_at IS NULL
                """,
                (reader_card_id,),
            )
            active_for_reader = cur.fetchone()[0]
            if active_for_reader >= max_books:
                raise ValueError(f"☠️❌ Pasiektas paimtų knygų limitas. Galima pasiimti tik {max_books} knygas")

            # if has overdue
            if self.reader_has_overdue(reader_card_id):
                raise ValueError("☠️❌ Negalima pasiimti knygos: turite vėluojančią knygą!")

            # if no available copies
            if self.available_copies(book_id) <= 0:
                raise ValueError("☠️❌ Šiuo metu nėra laisvų šios knygos kopijų.")

            borrow_date = self.now()
            return_date = borrow_date + dt.timedelta(days=days)

            cur.execute(
                """
                INSERT INTO loans (book_id, reader_card_id, borrow_date, return_date, returned_at)
                VALUES (?, ?, ?, ?, NULL)
                """,
                (str(book_id), reader_card_id, self._dt_to_text(borrow_date), self._dt_to_text(return_date)),
            )

            # for statistics
            genre = book_row[1]
            self.borrowed_genre_counts[genre] = self.borrowed_genre_counts.get(genre, 0) + 1

        return Loan(book_id, reader_card_id, borrow_date, return_date)


    def return_book(self, reader_card_id, book_id):
        returned_at = self._dt_to_text(self.now())

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE loans
                SET returned_at = ?
                WHERE reader_card_id = ? AND book_id = ? AND returned_at IS NULL
                """,
                (returned_at, reader_card_id, str(book_id)),
            )
            if cur.rowcount == 0:
                raise ValueError("☠️❌ Šis skaitytojas nėra paėmęs šios knygos.")

    
    # Delspinigiu skaiciavimas
    def calculate_fine(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        now_text = self._dt_to_text(now)
        fine_one_day = 0.5

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT return_date
                FROM loans
                WHERE reader_card_id = ? AND returned_at IS NULL AND return_date < ?
                """,
                (reader_card_id, now_text),
            )
            rows = cur.fetchall()

        overdue_days = 0
        for (return_text,) in rows:
            due = self._text_to_dt(return_text)
            overdue_days += (now - due).days

        fine = fine_one_day * overdue_days
        return fine, overdue_days


    # ----- Library statistics -----
    def statistics(self, now=None):
        if now is None:
            now = self.now()

        with self._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM books")
            total_books = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(SUM(copies), 0) FROM books")
            total_copies = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM loans WHERE returned_at IS NULL")
            total_loans = cur.fetchone()[0]

            now_text = self._dt_to_text(now)
            cur.execute(
                "SELECT COUNT(*) FROM loans WHERE returned_at IS NULL AND return_date < ?",
                (now_text,),
            )
            overdue_count = cur.fetchone()[0]

            # most common genre
            cur.execute(
                """
                SELECT genre, COUNT(*) as c
                FROM books
                GROUP BY genre
                ORDER BY c DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()
            most_common_genre = row[0] if row else None

        most_borrowed_genre = max(self.borrowed_genre_counts, key=self.borrowed_genre_counts.get) if self.borrowed_genre_counts else None

        # avg overdue days
        overdue_loans = self.list_overdue_loans(now)
        if not overdue_loans:
            avg_overdue_days = 0
        else:
            total_days = 0
            for loan in overdue_loans:
                total_days += (now - loan.return_date).days
            avg_overdue_days = total_days / len(overdue_loans)

        return {
            "total_books": total_books,
            "total_copies": total_copies,
            "total_loans": total_loans,
            "overdue_count": overdue_count,
            "avg_overdue_days": avg_overdue_days,
            "most_common_genre": most_common_genre,
            "most_borrowed_genre": most_borrowed_genre,
        }