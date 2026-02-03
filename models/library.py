import uuid
import datetime as dt
import random
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from services.db import SessionMaker
from models.orm_models import BookORM, ReaderORM, LibrarianORM, LoanORM

from models.book import Book
from models.reader import Reader
from models.librarian import Librarian
from models.loan import Loan
from config import MAX_BOOKS_PER_READER, DEFAULT_LOAN_DAYS


class Library:
    def __init__(self):
        self.starter_pack_added = False
        self.current_date = dt.datetime.now()
        self.borrowed_genre_counts = {}

    def now(self):
        return self.current_date

    def set_current_date(self, year, month, day):
        self.current_date = dt.datetime(year, month, day)

        # statistikai
        self.borrowed_genre_counts = {}



    # ---------- DB helpers ----------

    def _dt_to_text(self, value):
    # MySQL accepts datetime directly, so just return it
        return value


    def _text_to_dt(self, value):
        # MySQL often returns datetime already
        if value is None:
            return None
        if isinstance(value, dt.datetime):
            return value
        # fallback if something returns text
        return dt.datetime.fromisoformat(value)
    

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
            with SessionMaker() as session:
                session.add(LibrarianORM(user_name=user_name, password=password))
                session.commit()
        except IntegrityError:
            raise ValueError("☠️❌ Toks bibliotekininkas jau egzistuoja.")

        return Librarian(user_name, password)
    

    def authenticate_librarian(self, user_name, password):
        user_name = user_name.strip()
        password = password.strip()

        with SessionMaker() as session:
            stmt = select(LibrarianORM).where(LibrarianORM.user_name == user_name)
            row = session.execute(stmt).scalars().first()

        if not row:
            return None
        if row.password != password:
            return None

        return Librarian(row.user_name, row.password)
    

    def _generate_reader_card_id(self, name, last_name):
        initials = (name[:1] + last_name[:1]).upper()

        while True:
            digits = str(random.randint(0, 999999)).zfill(6)
            card_id = f"{initials}-{digits}"

            with SessionMaker() as session:
                exists = session.execute(
                    select(ReaderORM.card_id).where(ReaderORM.card_id == card_id)
                ).first()

            if not exists:
                return card_id
    
    
    def register_reader(self, name, last_name, password):
        name = name.strip()
        last_name = last_name.strip()
        password = password.strip()

        if not name or not last_name or not password:
            raise ValueError("☠️❌ Vardas, pavardė ir slaptažodis negali būti tušti.")

        card_id = self._generate_reader_card_id(name, last_name)

        with SessionMaker() as session:
            session.add(
                ReaderORM(card_id=card_id, name=name, last_name=last_name, password=password)
            )
            session.commit()

        r = Reader(name, last_name, card_id, password)
        r.taken_book_ids = self._get_taken_book_ids(card_id)  # should be empty for new reader
        return r
    

    def authenticate_reader(self, card_id, password):
        card_id = card_id.strip()
        password = password.strip()

        with SessionMaker() as session:
            row = session.execute(
                select(ReaderORM).where(ReaderORM.card_id == card_id)
            ).scalars().first()

        if not row:
            return None
        if row.password != password:
            return None

        r = Reader(row.name, row.last_name, row.card_id, row.password)
        r.taken_book_ids = self._get_taken_book_ids(row.card_id)
        return r



    # ----- Library services -----

    def get_book_by_id(self, book_id):
        book_id_text = str(book_id)

        with SessionMaker() as session:
            row = session.execute(
                select(BookORM).where(BookORM.id == book_id_text)
            ).scalars().first()

        if not row:
            return None

        b = Book(row.name, row.author, row.year, row.genre, copies=row.copies)
        b.id = uuid.UUID(row.id)
        return b



    def _get_taken_book_ids(self, reader_card_id):
        with SessionMaker() as session:
            rows = session.execute(
                select(LoanORM.book_id).where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.returned_at.is_(None),
                )
            ).all()

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

        with SessionMaker() as session:
            stmt = select(BookORM).where(
                func.lower(BookORM.name) == name.lower(),
                func.lower(BookORM.author) == author.lower(),
                BookORM.year == year,
            )
            existing = session.execute(stmt).scalars().first()

            if existing:
                existing.copies += copies
                session.commit()

                b = Book(existing.name, existing.author, existing.year, existing.genre, copies=existing.copies)
                b.id = uuid.UUID(existing.id)
                return b

            new_id = str(uuid.uuid4())
            new_book = BookORM(
                id=new_id, name=name, author=author, year=year, genre=genre, copies=copies
            )
            session.add(new_book)
            session.commit()

        b = Book(name, author, year, genre, copies=copies)
        b.id = uuid.UUID(new_id)
        return b


    def list_all_books(self):
        with SessionMaker() as session:
            stmt = select(BookORM).order_by(BookORM.name)
            rows = session.execute(stmt).scalars().all()

        books = []
        for r in rows:
            b = Book(r.name, r.author, r.year, r.genre, copies=r.copies)
            b.id = uuid.UUID(r.id)
            books.append(b)
        return books
    

    def search_books(self, text):
        text = text.strip().lower()
        if text == "":
            return []

        like = f"%{text}%"

        with SessionMaker() as session:
            rows = session.execute(
                select(BookORM).where(
                    func.lower(BookORM.name).like(like) | func.lower(BookORM.author).like(like)
                ).order_by(BookORM.name)
            ).scalars().all()

        books = []
        for row in rows:
            b = Book(row.name, row.author, row.year, row.genre, copies=row.copies)
            b.id = uuid.UUID(row.id)
            books.append(b)
        return books
    


    # ---------- Copies / availability ----------
    def borrowed_copies_count(self, book_id):
        book_id_text = str(book_id)

        with SessionMaker() as session:
            stmt = select(func.count()).select_from(LoanORM).where(
                LoanORM.book_id == book_id_text,
                LoanORM.returned_at.is_(None),
            )
            return session.execute(stmt).scalar_one()
    

    def available_copies(self, book_id):
        book_id_text = str(book_id)

        with SessionMaker() as session:
            copies_row = session.execute(
                select(BookORM.copies).where(BookORM.id == book_id_text)
            ).first()

            if not copies_row:
                return 0

            total_copies = copies_row[0]

            borrowed = session.execute(
                select(func.count()).select_from(LoanORM).where(
                    LoanORM.book_id == book_id_text,
                    LoanORM.returned_at.is_(None),
                )
            ).scalar_one()

        return total_copies - borrowed
    

    def list_available_books(self):
        books = self.list_all_books()
        available = []
        for b in books:
            if self.available_copies(b.id) > 0:
                available.append(b)
        return available


    def delete_old_books(self, oldest_possible_year):
        deleted = 0

        with SessionMaker() as session:
            # get all candidate book ids (old books)
            old_books = session.execute(
                select(BookORM.id, BookORM.year).where(BookORM.year < oldest_possible_year)
            ).all()

            for book_id_text, year in old_books:
                active = session.execute(
                    select(func.count()).select_from(LoanORM).where(
                        LoanORM.book_id == book_id_text,
                        LoanORM.returned_at.is_(None),
                    )
                ).scalar_one()

                if active == 0:
                    # delete book row
                    session.execute(
                        BookORM.__table__.delete().where(BookORM.id == book_id_text)
                    )
                    deleted += 1

            session.commit()

        return deleted
    


    # ----- metodai knygų išdavimui / gražinimui ir negražintų knygų patikrai -----
    def reader_has_overdue(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        with SessionMaker() as session:
            exists = session.execute(
                select(LoanORM.id).where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.returned_at.is_(None),
                    LoanORM.return_date < now,
                ).limit(1)
            ).first()

        return exists is not None
    

    def list_overdue_loans(self, now=None):
        if now is None:
            now = self.now()

        with SessionMaker() as session:
            rows = session.execute(
                select(LoanORM).where(
                    LoanORM.returned_at.is_(None),
                    LoanORM.return_date < now,
                ).order_by(LoanORM.return_date)
            ).scalars().all()

        loans = []
        for row in rows:
            loan = Loan(
                uuid.UUID(row.book_id),
                row.reader_card_id,
                row.borrow_date,
                row.return_date,
            )
            loans.append(loan)

        return loans


    def overdue_count_for_reader_meniu(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        with SessionMaker() as session:
            count = session.execute(
                select(func.count()).select_from(LoanORM).where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.returned_at.is_(None),
                    LoanORM.return_date < now,
                )
            ).scalar_one()

        return count


    def find_loan(self, reader_card_id, book_id):
        book_id_text = str(book_id)

        with SessionMaker() as session:
            row = session.execute(
                select(LoanORM).where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.book_id == book_id_text,
                    LoanORM.returned_at.is_(None),
                )
            ).scalars().first()

        if not row:
            return None

        return Loan(
            uuid.UUID(row.book_id),
            row.reader_card_id,
            row.borrow_date,
            row.return_date,
        )



    def lend_book(self, reader_card_id, book_id, days=DEFAULT_LOAN_DAYS, max_books=MAX_BOOKS_PER_READER):
 
        book_id_text = str(book_id)

        with SessionMaker() as session:
            # validate reader exists
            reader_exists = session.execute(
                select(ReaderORM.card_id).where(ReaderORM.card_id == reader_card_id)
            ).first()
            if not reader_exists:
                raise ValueError("☠️❌ Nerastas skaitytojas su tokiu kortelės numeriu.")

            # validate book exists + get genre
            book_row = session.execute(
                select(BookORM.copies, BookORM.genre).where(BookORM.id == book_id_text)
            ).first()
            if not book_row:
                raise ValueError("☠️❌ Nerasta tokia knyga.")

            if days <= 0:
                raise ValueError("☠️❌ Dienų skaičius turi būti teigiamas.")

            # max books limit reached?
            active_for_reader = session.execute(
                select(func.count())
                .select_from(LoanORM)
                .where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.returned_at.is_(None),
                )
            ).scalar_one()

            if active_for_reader >= max_books:
                raise ValueError(f"☠️❌ Pasiektas paimtų knygų limitas. Galima pasiimti tik {max_books} knygas")

            # overdue block
            if self.reader_has_overdue(reader_card_id):
                raise ValueError("☠️❌ Negalima pasiimti knygos: turite vėluojančią knygą!")

            # available copies check
            if self.available_copies(book_id) <= 0:
                raise ValueError("☠️❌ Šiuo metu nėra laisvų šios knygos kopijų.")

            borrow_date = self.now()
            return_date = borrow_date + dt.timedelta(days=days)

            session.add(
                LoanORM(
                    book_id=book_id_text,
                    reader_card_id=reader_card_id,
                    borrow_date=borrow_date,
                    return_date=return_date,
                    returned_at=None,
                )
            )
            session.commit()

            # statistics (same as your old code)
            genre = book_row[1]
            self.borrowed_genre_counts[genre] = self.borrowed_genre_counts.get(genre, 0) + 1

        return Loan(book_id, reader_card_id, borrow_date, return_date)


    def return_book(self, reader_card_id, book_id):
        returned_at = self.now()
        book_id_text = str(book_id)

        with SessionMaker() as session:
            loan = session.execute(
                select(LoanORM).where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.book_id == book_id_text,
                    LoanORM.returned_at.is_(None),
                )
            ).scalars().first()

            if not loan:
                raise ValueError("☠️❌ Šis skaitytojas nėra paėmęs šios knygos.")

            loan.returned_at = returned_at
            session.commit()

    
    # Delspinigiu skaiciavimas
    def calculate_fine(self, reader_card_id, now=None):
        if now is None:
            now = self.now()

        fine_one_day = 0.5

        with SessionMaker() as session:
            rows = session.execute(
                select(LoanORM.return_date).where(
                    LoanORM.reader_card_id == reader_card_id,
                    LoanORM.returned_at.is_(None),
                    LoanORM.return_date < now,
                )
            ).all()

        overdue_days = 0
        for (due_date,) in rows:
            overdue_days += (now - due_date).days

        fine = fine_one_day * overdue_days
        return fine, overdue_days


    # ----- Library statistics -----
    def statistics(self, now=None):
        if now is None:
            now = self.now()

        with SessionMaker() as session:
            total_books = session.execute(
                select(func.count()).select_from(BookORM)
            ).scalar_one()

            total_copies = session.execute(
                select(func.coalesce(func.sum(BookORM.copies), 0))
            ).scalar_one()

            total_loans = session.execute(
                select(func.count()).select_from(LoanORM).where(LoanORM.returned_at.is_(None))
            ).scalar_one()

            overdue_count = session.execute(
                select(func.count()).select_from(LoanORM).where(
                    LoanORM.returned_at.is_(None),
                    LoanORM.return_date < now,
                )
            ).scalar_one()

            # most common genre
            row = session.execute(
                select(BookORM.genre, func.count().label("c"))
                .group_by(BookORM.genre)
                .order_by(func.count().desc())
                .limit(1)
            ).first()

            most_common_genre = row[0] if row else None

        most_borrowed_genre = (
            max(self.borrowed_genre_counts, key=self.borrowed_genre_counts.get)
            if self.borrowed_genre_counts else None
        )

        # avg overdue days (reuse your existing list_overdue_loans())
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