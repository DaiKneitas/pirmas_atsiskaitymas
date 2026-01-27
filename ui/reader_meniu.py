from uuid import UUID
from utils.helper_functions import _input_text, _ask_choice, _ask_int, _clear_screen
from utils.print_tables import _print_books_table, _print_overdue_table
from config import MAX_BOOKS_PER_READER, DEFAULT_LOAN_DAYS


def reader_meniu(library, reader):
    last_message = ""

    while True:
        _clear_screen()

        # refresh taken ids from DB (important in DB mode)
        reader.taken_book_ids = library._get_taken_book_ids(reader.reader_card_id)

        taken_count = len(reader.taken_book_ids)
        overdue_count = library.overdue_count_for_reader_meniu(reader.reader_card_id)

        if last_message:
            print(last_message)
            print()

        selection = _ask_choice(f"""
--------------------------------------------------------------------
Sveiki prisijungę prie bibliotekos!
Prisijungęs skaitytojas: {reader.name}
Paimtų knygų kiekis: {taken_count} | Vėluojančių knygų kiekis: {overdue_count}

Įveskite skaičių esantį prie vieno iš šių galimų veiksmų:

1) Pasiimti knygą išsinešimui
2) Peržiūrėti / gražinti pasiimtas knygas
3) Pasitikrinti ar nėra vėluojančių knygų
4) Peržiūrėti visas bibliotekos knygas
5) Ieškoti knygų bibliotekoje, pagal knygos pavadinimą arba autorių.
6) Pažiūrėti kiek yra priskaičiuota delspinigių
--------------------------------------------------------------------
9) Atsijungti
--------------------------------------------------------------------
""", {"1", "2", "3", "4", "5", "6", "9"})

        # 1) Borrow
        if selection == "1":
            try:
                fine, overdue_days = library.calculate_fine(reader.reader_card_id)
                if overdue_days > 0:
                    last_message = f"☠️❌ Turite vėluojančių knygų ({overdue_days} d.) ir delspinigių {fine:.2f} EUR!"
                    continue

                available_books = library.list_available_books()
                if not available_books:
                    last_message = "☠️❌ Šiuo metu nėra laisvų knygų."
                    continue

                _print_books_table(library, available_books)

                book_id_text = _input_text("\nĮveskite knygos ID: ").strip()
                try:
                    book_id = UUID(book_id_text)
                except ValueError:
                    last_message = "☠️❌ Neteisingas ID formatas."
                    continue

                days = _ask_int(
                    f"Kiek dienų norite pasiimti knygą? (max galima {DEFAULT_LOAN_DAYS}): ",
                    min_value=1,
                    max_value=DEFAULT_LOAN_DAYS,
                )

                library.lend_book(
                    reader.reader_card_id,
                    book_id,
                    days=days,
                    max_books=MAX_BOOKS_PER_READER,
                )

                last_message = "✅ Knyga sėkmingai paimta!"

            except Exception as e:
                last_message = f"☠️❌ Klaida: {e}"

        # 2) List / return borrowed books
        elif selection == "2":
            taken = reader.taken_book_ids
            if not taken:
                last_message = "Neturite pasiimtų knygų."
                continue

            print("Jūsų pasiimtos knygos:")
            for book_id in taken:
                # Get book data by searching list_all_books (simple, minimal change)
                # (If you want, later we can add db_get_book_by_id for speed)
                all_books = library.list_all_books()
                book = next((b for b in all_books if b.id == book_id), None)

                if book:
                    loan = library.find_loan(reader.reader_card_id, book_id)
                    if loan:
                        print(f"{book.name} — {book.author} | grąžinti iki: {loan.return_date.date()} | id={book.id}")
                    else:
                        print(f"{book.name} — {book.author} | id={book.id}")

            answer = _ask_choice("\nAr norite grąžinti knygą? (1-Taip, 2-Ne): ", {"1", "2"})
            if answer == "1":
                book_id_text = _input_text("Įveskite knygos ID grąžinimui: ").strip()
                try:
                    book_id = UUID(book_id_text)
                except ValueError:
                    last_message = "☠️❌ Neteisingas ID formatas."
                    continue

                try:
                    library.return_book(reader.reader_card_id, book_id)
                    last_message = "✅ Knyga sėkmingai grąžinta."
                except Exception as e:
                    last_message = f"☠️❌ Klaida: {e}"
            else:
                last_message = ""

        # 3) Overdue check (reader only)
        elif selection == "3":
            overdue_all = library.list_overdue_loans()
            overdue_reader = []

            for loan in overdue_all:
                if loan.reader_card_id == reader.reader_card_id:
                    overdue_reader.append(loan)

            _print_overdue_table(library, overdue_reader)

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        # 4) List all books
        elif selection == "4":
            books = library.list_all_books()
            _print_books_table(library, books)

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        # 5) Search
        elif selection == "5":
            text = _input_text("Įveskite pavadinimą arba autorių: ")
            results = library.search_books(text)

            if not results:
                print("Nerasta.")
            else:
                _print_books_table(library, results)

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        # 6) Fine
        elif selection == "6":
            fine, overdue_days = library.calculate_fine(reader.reader_card_id)

            print(
                f"Priskaičiuoti delspinigiai: {fine:.2f} EUR.\n"
                f"Delspinigių dienos: {overdue_days}"
            )

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        # 9) Logout
        elif selection == "9":
            return


