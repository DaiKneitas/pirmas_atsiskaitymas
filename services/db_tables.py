import sqlite3


def get_connection(db_path):
    return sqlite3.connect(db_path)


def library_tables(db_path):
    with get_connection(db_path) as conn:
        cur = conn.cursor()

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    year INTEGER NOT NULL,
                    genre VARCHAR(60) NOT NULL,
                    copies INTEGER NOT NULL
                    )
                    """)
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS readers (
                    card_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(60) NOT NULL,
                    last_name VARCHAR(60) NOT NULL,
                    password VARCHAR(100) NOT NULL
                    )
                    """)
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS librarians (
                    user_name VARCHAR(60) PRIMARY KEY,
                    password VARCHAR(100) NOT NULL
                    )
                    """)
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id VARCHAR(36) NOT NULL,
                    reader_card_id VARCHAR(20) NOT NULL,
                    borrow_date TEXT NOT NULL,
                    return_date TEXT NOT NULL,
                    returned_at TEXT,
                    FOREIGN KEY(book_id) REFERENCES books(id),
                    FOREIGN KEY(reader_card_id) REFERENCES readers(card_id)
                    )
                    """)
