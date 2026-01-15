# reader_meniu.py

from utils.helper_functions import _input_text, _ask_choice, _ask_int

def reader_meniu(library, reader, save):
    while True:
        selection = _ask_choice("""
Sveiki prisijungę prie bibliotekos!
Įveskite skaičių esantį prie vieno iš šių galimų veiksmų:

1) Pasiimti knygą išsinešimui
2) Peržiūrėti pasiimtas knygas
3) Pasitikrinti ar nėra vėluojančių knygų
4) Peržiūrėti visas bibliotekos knygas
5) Ieškoti knygų bibliotekoje, pagal knygos pavadinimą arba autorių.
--------------------------------------------------------------------
9) Atsijungti
""", {"1","2","3","4","5","9"})
        
        if selection == "1":
            pass

        elif selection == "2":
            pass

        elif selection == "3":
            pass

        elif selection == "4":
            books = library.list_all_books()
            if not books:
                print("Įvyko gaisras!!! Knygų bibliotekoje nebėra!")
            for b in books:
                print(f"{b.name} — {b.author} ({b.year}) [{b.genre}] | kopijos={b.copies} |")

        elif selection == "5":
            text = _input_text("Įveskite pavadinimą arba autorių: ")
            results = library.search_books(text)
            if not results:
                print("Nerasta.")
            for b in results:
                available = library.available_copies(b.id)
                status = "LAISVA" if available > 0 else "PAIMTA"
                print(f"{b.name} — {b.author} ({b.year}) | {status} | laisva {available}/{b.copies} | id={b.id}")

        elif selection == "9":
            return
