def _print_books_table(library, books):
    if not books:
        print("😱 Bibliotekoje įvyko gaisras. Viskas sudegė. Knygų nebėra...")
        return

    W_NAME = 30
    W_AUTHOR = 22
    W_YEAR = 6
    W_GENRE = 18
    W_STATUS = 8
    W_COPIES = 5

    header = (
        f"{'Pavadinimas':<{W_NAME}} | {'Autorius':<{W_AUTHOR}} | "
        f"{'Metai':<{W_YEAR}} | {'Žanras':<{W_GENRE}} | "
        f"{'Statusas':<{W_STATUS}} | {'Kop.':<{W_COPIES}} | ID"
    )
    print(header)
    print("-" * len(header))

    for book in books:
        available = library.available_copies(book.id)
        status = "LAISVA" if available > 0 else "PAIMTA"

        name = book.name[:W_NAME]
        author = book.author[:W_AUTHOR]
        genre = book.genre[:W_GENRE]
        copies_text = f"{available}/{book.copies}"

        row = (
            f"{name:<{W_NAME}} | "
            f"{author:<{W_AUTHOR}} | "
            f"{book.year:<{W_YEAR}} | "
            f"{genre:<{W_GENRE}} | "
            f"{status:<{W_STATUS}} | "
            f"{copies_text:<{W_COPIES}} | "
            f"{book.id}"
        )
        print(row)


def _print_overdue_table(library, overdue_loans):
    if not overdue_loans:
        print("✅ Vėluojančių knygų nėra.")
        return

    W_NAME = 30
    W_AUTHOR = 22
    W_CARD = 12
    W_DUE = 12

    header = (
        f"{'Pavadinimas':<{W_NAME}} | {'Autorius':<{W_AUTHOR}} | "
        f"{'Kortelė':<{W_CARD}} | {'Terminas':<{W_DUE}} | ID"
    )
    print(header)
    print("-" * len(header))

    for loan in overdue_loans:
        book = library.get_book_by_id(loan.book_id)
        if not book:
            continue

        name = book.name[:W_NAME]
        author = book.author[:W_AUTHOR]
        due = str(loan.return_date.date())

        row = (
            f"{name:<{W_NAME}} | "
            f"{author:<{W_AUTHOR}} | "
            f"{loan.reader_card_id:<{W_CARD}} | "
            f"{due:<{W_DUE}} | "
            f"{loan.book_id}"
        )
        print(row)

