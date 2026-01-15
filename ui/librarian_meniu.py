from utils.helper_functions import _input_text, _ask_choice

def librarian_meniu(library, librarian):
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
8) Pridėti startinį knygų paketą į biblioteką (10 knygų)
9) Atsijungti
""", {"1","2","3","4","5","8","9"})

        if selection == "1":
            pass

        elif selection == "2":
            pass

        elif selection == "3":
            pass

        elif selection == "4":
            pass

        elif selection == "5":
            pass

        elif selection == "8":
            pass

        elif selection == "9":
            return None
