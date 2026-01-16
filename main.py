import os

def main():
	try:
		from models.library import Library
		from services.storage import load_file, save_file
		from ui.login_meniu import login_meniu
		from ui.librarian_meniu import librarian_meniu
		from ui.reader_meniu import reader_meniu
		from config import DATA_FILE, DEFAULT_LIBRARIAN_USERNAME, DEFAULT_LIBRARIAN_PASSWORD

		os.makedirs("data", exist_ok=True)

		library = load_file(DATA_FILE)
		if library is None:
			library = Library()

		def save():
			save_file(DATA_FILE, library)

		if not library.librarians:
			library.add_librarian(DEFAULT_LIBRARIAN_USERNAME, DEFAULT_LIBRARIAN_PASSWORD)
			save()

		while True:
			session = login_meniu(library, save)

			if session is None:
				save()
				print("Programa uždaroma")
				break

			role, user_obj = session

			if role == "librarian":
				librarian_meniu(library, user_obj, save)

			elif role == "reader":
				reader_meniu(library, user_obj, save)
	except Exception as e:
		print(f"😱☠️ Klaida: {e}")


if __name__ == "__main__":
    main()
