import pymysql
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
 
def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        autocommit=True,
    )  


# -------- mysql table -----------
def library_tables():
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                author VARCHAR(100) NOT NULL,
                year INT NOT NULL,
                genre VARCHAR(60) NOT NULL,
                copies INT NOT NULL
            ) ENGINE=InnoDB;
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS readers (
                card_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(60) NOT NULL,
                last_name VARCHAR(60) NOT NULL,
                password VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB;
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS librarians (
                user_name VARCHAR(60) PRIMARY KEY,
                password VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB;
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INT PRIMARY KEY AUTO_INCREMENT,
                book_id VARCHAR(36) NOT NULL,
                reader_card_id VARCHAR(20) NOT NULL,
                borrow_date DATETIME NOT NULL,
                return_date DATETIME NOT NULL,
                returned_at DATETIME NULL,
                CONSTRAINT fk_loans_book
                    FOREIGN KEY (book_id) REFERENCES books(id),
                CONSTRAINT fk_loans_reader
                    FOREIGN KEY (reader_card_id) REFERENCES readers(card_id)
            ) ENGINE=InnoDB;
        """)

    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()
