import datetime as dt
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BookORM(Base):
    __tablename__ = "library_books"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    genre: Mapped[str] = mapped_column(String(60), nullable=False)
    copies: Mapped[int] = mapped_column(Integer, nullable=False)

    loans: Mapped[list["LoanORM"]] = relationship(back_populates="book")


class ReaderORM(Base):
    __tablename__ = "library_readers"

    card_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    loans: Mapped[list["LoanORM"]] = relationship(back_populates="reader")


class LibrarianORM(Base):
    __tablename__ = "library_librarians"

    user_name: Mapped[str] = mapped_column(String(60), primary_key=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)


class LoanORM(Base):
    __tablename__ = "library_loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    book_id: Mapped[str] = mapped_column(ForeignKey("library_books.id"), nullable=False)
    reader_card_id: Mapped[str] = mapped_column(ForeignKey("library_readers.card_id"), nullable=False)

    borrow_date: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    return_date: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    returned_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    book: Mapped["BookORM"] = relationship(back_populates="loans")
    reader: Mapped["ReaderORM"] = relationship(back_populates="loans")
