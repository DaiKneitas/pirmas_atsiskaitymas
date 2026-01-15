# librarian_meniu.py

from utils.helper_functions import _input_text, _ask_choice, _ask_int
from starter_books.starter_books import starter_books

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
6) Peržiūrėti bibliotekos statistiką
--------------------------------------------------------------------
8) Pridėti startinį knygų paketą į biblioteką (100 skirtingų knygų)
9) Atsijungti
""", {"1","2","3","4","5","6","8","9"})

        if selection == "1":
            try:
                name = _input_text("Pavadinimas: ").strip()
                author = _input_text("Autorius: ").strip()
                year = _ask_int("Metai: ", min_value=-5000, max_value=2100)
                genre = _input_text("Žanras: ").strip()
                copies = _ask_int("Kopijų skaičius: ", min_value=1)

                book = library.add_book(name, author, year, genre, copies=copies)
                save()
                print(f"Knyga pridėta. ID: {book.id}")

            except Exception as e:
                print(f"Klaida: {e}")

        elif selection == "2":
            older_than = _ask_int("Pašalinti knygas senesnes nei (metai): ", min_value=-5000, max_value=2100)
            deleted = library.delete_old_books(older_than)
            print(f"Pašalinta knygų: {deleted}")
            save()

        elif selection == "3":
            books = library.list_all_books()
            if not books:
                print("Įvyko gaisras!!! Knygų bibliotekoje nebėra!")
            for b in books:
                print(f"{b.name} — {b.author} ({b.year}) [{b.genre}] | kopijos={b.copies} |")


        elif selection == "4":
            overdue = library.list_overdue_loans()
            if not overdue:
                print("Vėluojančių knygų nėra.")
            for loan in overdue:
                b = library.books[loan.book_id]
                print(f"VĖLUOJA: {b.name} — {b.author} | kortelė={loan.reader_card_id} | terminas={loan.return_date.date()}")


        elif selection == "5":
            text = _input_text("Įveskite pavadinimą arba autorių: ")
            results = library.search_books(text)
            if not results:
                print("Nerasta.")
            for b in results:
                available = library.available_copies(b.id)
                status = "LAISVA" if available > 0 else "PAIMTA"
                print(f"{b.name} — {b.author} ({b.year}) | {status} | laisva {available}/{b.copies} | id={b.id}")


        elif selection == "6":
            stats = library.statistics()

            most_common = stats["most_common_genre"]
            if most_common is None:
                most_common = "Nėra duomenų"

            most_borrowed = stats["most_borrowed_genre"]
            if most_borrowed is None:
                most_borrowed = "Nėra duomenų"

            print("---- Statistika ----")
            print(f"Viso knygų: {stats['total_books']}")
            print(f"Išduotų knygų kiekis: {stats['total_loans']}")
            print(f"Vėluojančių negražintų knygų: {stats['overdue_count']}")
            print(f"Vid. vėlavimo dienos: {stats['avg_overdue_days']:.2f}")
            print(f"Kokio žanro knygų yra daugiausiai bibliotekoje: {most_common}")
            print(f"Kokio žanro knygos yra daugiausiai imamos: {most_borrowed}")


        elif selection == "8":
            if library.starter_pack_added:
                print("Startinis knygų paketas jau buvo pridėtas.")
                return
            
            try:
                added = 0
                for b in starter_books:
                    library.add_book(b["name"], b["author"], b["year"], b["genre"], b["copies"])
                    added += 1
                
                library.starter_pack_added = True
                save()
                print(f"Pridėtas startinis knygų paketas. Pridėta knygų: {added}")

            except Exception as e:
                print(f"Klaida: {e}")

        elif selection == "9":
            return
