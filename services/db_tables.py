import sqlite3


def get_connection(db_path):
    return sqlite3.connect(db_path)


def library_tables(db_path):
    with get_connection(db_path) as conn:
        cur = conn.cursor()

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                    ID VARCHAR(36) PRIMARY KEY,
                    NAME VARCHAR(100) NOT NULL,
                    AUTHOR VARCHAR(100) NOT NULL,
                    YEAR INTEGER NOT NULL,
                    GENRE VARCHAR(60) NOT NULL,
                    COPIES INTEGER NOT NULL
                    )
                    """)
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS readers (
                    CARD_ID VARCHAR(20) PRIMARY KEY,
                    NAME VARCHAR(60) NOT NULL,
                    LAST_NAME VARCHAR(60) NOT NULL,
                    PASSWORD VARCHAR(100) NOT NULL
                    )
                    """)
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS librarians (
                    USER_NAME VARCHAR(60) PRIMARY KEY,
                    PASSWORD VARCHAR(100) NOT NULL
                    )
                    """)
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS loans (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    BOOK_ID VARCHAR(36) NOT NULL,
                    READER_CARD_ID VARCHAR(20) NOT NULL,
                    BORROW_DATE TEXT NOT NULL,
                    RETURN_DATE TEXT NOT NULL,
                    FOREIGN KEY(BOOK_ID) REFERENCES books(ID),
                    FOREIGN KEY(READER_CARD_ID) REFERENCES readers(CARD_ID)
                    )
                    """)
