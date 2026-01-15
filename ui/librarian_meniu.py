# librarian_meniu.py

from utils.helper_functions import _input_text, _ask_choice, _ask_int
from data.starter_books import starter_books

def librarian_meniu(library, librarian, save):
    while True:
        selection = _ask_choice("""
Bibliotekos valdymas
Įveskite skaičių esantį prie vieno iš šių galimų veiksmų:

1) Pridėti naują knygą į biblioteką
2) Pašalinti senas/nebenaudojamas knygas
3) Peržiūrėti visas bibliotekos knygas
4) Peržiūrėti visas vėluojančias knygas
5) Ieškoti knygų bibliotekoje, pagal knygos pavadinimą arba autorių.
--------------------------------------------------------------------
8) Pridėti startinį knygų paketą į biblioteką (10 knygų iš starter_books failo)
9) Atsijungti
""", {"1","2","3","4","5","8","9"})

        if selection == "1":
            try:
                name = _input_text("Pavadinimas: ").strip()
                author = _input_text("Autorius: ").strip()
                year = _ask_int("Metai: ", min_value=0)
                genre = _input_text("Žanras: ").strip()
                copies = _ask_int("Kopijų skaičius: ", min_value=1)

                book = library.add_book(name, author, year, genre, copies=copies)
                save()
                print(f"Knyga pridėta. ID: {book.id}")

            except Exception as e:
                print(f"Klaida: {e}")

        elif selection == "2":
            pass

        elif selection == "3":
            books = library.list_all_books()
            if not books:
                print("Įvyko gaisras!!! Knygų bibliotekoje nebėra!")
            for b in books:
                print(f"{b.name} — {b.author} ({b.year}) [{b.genre}] | kopijos={b.copies} | id={b.id}")

        elif selection == "4":
            pass

        elif selection == "5":
            pass

        elif selection == "8":
            try:
                added = 0
                for b in starter_books:
                    library.add_book(b["name"], b["author"], b["year"], b["genre"], copies=1)
                    added += 1

                save()
                print(f"Pridėtas startinis knygų paketas. Pridėta knygų: {added}")

            except Exception as e:
                print(f"Klaida: {e}")

        elif selection == "9":
            return
