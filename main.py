from models.library import Library
from services.db_tables import library_tables
from ui.login_meniu import login_meniu
from ui.librarian_meniu import librarian_meniu
from ui.reader_meniu import reader_meniu
from config import DB_FILE
import os


def main():
    os.makedirs("database_files", exist_ok=True)
    library_tables(DB_FILE)

    library = Library(DB_FILE)

    while True:
        session = login_meniu(library)
        if session is None:
            print("Programa uždaroma")
            break

        role, user_obj = session
        if role == "librarian":
            librarian_meniu(library, user_obj)
        else:
            reader_meniu(library, user_obj)


if __name__ == "__main__":
    main()

