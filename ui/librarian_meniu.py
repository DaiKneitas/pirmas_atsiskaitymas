from utils.helper_functions import _input_text, _ask_choice, _ask_int, _clear_screen
from utils.print_tables import _print_books_table, _print_overdue_table
from starter_books.starter_books import starter_books

def librarian_meniu(library, librarian, save):
    last_message = ""

    while True:
        _clear_screen()

        if last_message:
            print(last_message)
            print()

        selection = _ask_choice(f"""
--------------------------------------------------------------------
Bibliotekos valdymas
Prisijungęs bibliotekininkas: {librarian.user_name}
Bendras knygų kiekis (be kopijų): {len(library.books)} | Paimtų knygų kiekis: {len(library.loans)}



Įveskite skaičių esantį prie vieno iš šių galimų veiksmų:

1) Pridėti naują knygą į biblioteką
2) Pašalinti senas/nebenaudojamas knygas
3) Peržiūrėti visas bibliotekos knygas
4) Peržiūrėti visas vėluojančias knygas
5) Ieškoti knygų bibliotekoje, pagal knygos pavadinimą arba autorių.
6) Peržiūrėti bibliotekos statistiką
--------------------------------------------------------------------
7) Pakeisti dabartinę datą (testavimui)
8) Pridėti startinį knygų paketą į biblioteką (100 skirtingų knygų)
9) Atsijungti
--------------------------------------------------------------------
""", {"1","2","3","4","5","6","7","8","9"})

        if selection == "1":
            try:
                name = _input_text("Pavadinimas: ").strip()
                author = _input_text("Autorius: ").strip()
                year = _ask_int("Metai: ", min_value=-1000, max_value=2100)
                genre = _input_text("Žanras: ").strip()
                copies = _ask_int("Kopijų skaičius: ", min_value=1)

                book = library.add_book(name, author, year, genre, copies=copies)
                save()
                last_message = f"✅ Knyga pridėta / papildytos kopijos. ID: {book.id} | kopijos={book.copies}"

            except Exception as e:
                last_message = f"Klaida: {e}"

        elif selection == "2":
            try:
                older_than = _ask_int("Pašalinti knygas senesnes nei (metai): ", min_value=-1000, max_value=2101)
                deleted = library.delete_old_books(older_than)
                save()
                last_message = f"✅ Pašalinta knygų: {deleted}"
            except Exception as e:
                last_message = f"Klaida: {e}"

        elif selection == "3":
            books = library.list_all_books()
            _print_books_table(library, books)
            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""


        elif selection == "4":
            overdue = library.list_overdue_loans()
            _print_overdue_table(library, overdue)
            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""


        elif selection == "5":
            text = _input_text("Įveskite pavadinimą arba autorių: ")
            results = library.search_books(text)
            if not results:
                print("Nerasta.")
            else:
                _print_books_table(library, results)

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        elif selection == "6":
            stats = library.statistics()

            most_common = stats["most_common_genre"] or "Nėra duomenų"
            most_borrowed = stats["most_borrowed_genre"] or "Nėra duomenų"

            print("---- Statistika ----")
            print(f"Viso knygų bibliotekoje (be kopijų): {stats['total_books']}")
            print(f"Bendrai knygų bibliotekoje (su kopijomis): {stats['total_copies']}")
            print(f"Išduotų knygų kiekis: {stats['total_loans']}")
            print(f"Vėluojančių negražintų knygų: {stats['overdue_count']}")
            print(f"Kiek dienų vidutiniškai vėluoja knygos: {stats['avg_overdue_days']:.0f}")
            print(f"Kokio žanro knygų yra daugiausiai bibliotekoje: {most_common}")
            print(f"Kokio žanro knygos yra daugiausiai imamos: {most_borrowed}")
            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        elif selection == "7":
            try:
                print(f"Dabartinė data: {library.now().date()}")
                year = _ask_int("Įveskite metus: ", min_value=2026, max_value=3000)
                month = _ask_int("Įveskite mėnesį (1-12): ", min_value=1, max_value=12)
                day = _ask_int("Įveskite dieną (1-31): ", min_value=1, max_value=31)

                library.set_current_date(year, month, day)
                save()
                last_message = f"✅ Nauja dabartinė data: {library.now().date()}"

            except Exception as e:
                last_message = f"Neteisinga data: {e}"

        elif selection == "8":
            if library.starter_pack_added:
                last_message = "☠️❌ Startinis knygų paketas jau buvo pridėtas."
                continue

            try:
                added = 0
                for b in starter_books:
                    library.add_book(b["name"], b["author"], b["year"], b["genre"], b["copies"])
                    added += 1

                library.starter_pack_added = True
                save()
                last_message = f"✅ Pridėtas startinis knygų paketas. Pridėta knygų: {added}"

            except Exception as e:
                last_message = f"☠️❌ Klaida: {e}"

        elif selection == "9":
            return

