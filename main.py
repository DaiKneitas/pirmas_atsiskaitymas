from models.library import Library
from services.storage import load_file, save_file
from ui.login_meniu import login_meniu
from ui.librarian_meniu import librarian_meniu
from ui.reader_meniu import reader_meniu
from config import DATA_FILE, DEFAULT_LIBRARIAN_USERNAME, DEFAULT_LIBRARIAN_PASSWORD
import os


def main():
	os.makedirs("data", exist_ok=True)

	library = load_file(DATA_FILE)
	if library is None:
		library = Library()

	if not library.librarians:
		library.add_librarian(DEFAULT_LIBRARIAN_USERNAME, DEFAULT_LIBRARIAN_PASSWORD)
		save_file(DATA_FILE, library)

	login_meniu(library)

	print(library.librarians)
	print(library.readers)



main()
