from uuid import UUID
from utils.helper_functions import _input_text, _ask_choice, _ask_int, _clear_screen

def reader_meniu(library, reader, save):
    last_message = ""

    while True:
        _clear_screen()

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
--------------------------------------------------------------------
9) Atsijungti
--------------------------------------------------------------------
""", {"1","2","3","4","5","9"})

        if selection == "1":
            try:
                if library.reader_has_overdue(reader.reader_card_id):
                    last_message = "☠️❌ Turite vėluojančių knygų! Pirmiausia grąžinkite jas!"
                    continue

                available_books = library.list_available_books()
                if not available_books:
                    last_message = "☠️❌ Šiuo metu nėra laisvų knygų."
                    continue

                print("Laisvos knygos:")
                for b in available_books:
                    available = library.available_copies(b.id)
                    print(f"{b.name} — {b.author} ({b.year}) | laisva {available}/{b.copies} | id={b.id}")

                book_id_text = _input_text("\nĮveskite knygos ID: ").strip()
                try:
                    book_id = UUID(book_id_text)
                except Exception:
                    last_message = "☠️❌ Neteisingas ID formatas."
                    continue

                days = _ask_int("Kiek dienų norite pasiimti knygą? (pvz 14): ", min_value=1, max_value=365)

                library.lend_book(reader.reader_card_id, book_id, days=days, max_books=3)
                save()
                last_message = "✅ Knyga sėkmingai paimta!"

            except Exception as e:
                last_message = f"☠️❌ Klaida: {e}"

        elif selection == "2":
            taken = reader.taken_book_ids
            if not taken:
                last_message = "☠️❌ Neturite pasiimtų knygų."
                continue

            print("Jūsų pasiimtos knygos:")
            for book_id in taken:
                book = library.books.get(book_id)
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
                except Exception:
                    last_message = "☠️❌ Neteisingas ID formatas."
                    continue

                try:
                    library.return_book(reader.reader_card_id, book_id)
                    save()
                    last_message = "✅ Knyga sėkmingai grąžinta."
                except Exception as e:
                    last_message = f"☠️❌ Klaida: {e}"
            else:
                last_message = ""

        elif selection == "3":
            if library.reader_has_overdue(reader.reader_card_id):
                print("⏰ Turite vėluojančių knygų!")
                overdue_loans = library.list_overdue_loans()

                found_any = False
                for loan in overdue_loans:
                    if loan.reader_card_id == reader.reader_card_id:
                        book = library.books.get(loan.book_id)
                        if book:
                            print(f"VĖLUOJA: {book.name} — terminas buvo {loan.return_date.date()} | id={book.id}")
                            found_any = True

                if not found_any:
                    print("Vėluojančių paskolų nerasta (nors reader_has_overdue grąžino True).")

            else:
                print("✅ Vėluojančių knygų nėra.")

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        elif selection == "4":
            books = library.list_all_books()
            if not books:
                print("😱 Įvyko gaisras!!! Knygų bibliotekoje nebėra!")
            else:
                for b in books:
                    available = library.available_copies(b.id)
                    status = "LAISVA" if available > 0 else "PAIMTA"
                    print(f"{b.name} — {b.author} ({b.year}) [{b.genre}] | {status} | laisva {available}/{b.copies} | id={b.id}")

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        elif selection == "5":
            text = _input_text("Įveskite pavadinimą arba autorių: ")
            results = library.search_books(text)

            if not results:
                print("Nerasta.")
            else:
                for b in results:
                    available = library.available_copies(b.id)
                    status = "LAISVA" if available > 0 else "PAIMTA"
                    print(f"{b.name} — {b.author} ({b.year}) | {status} | laisva {available}/{b.copies} | id={b.id}")

            input("\nSpauskite Enter, kad grįžti į meniu...")
            last_message = ""

        elif selection == "9":
            return

