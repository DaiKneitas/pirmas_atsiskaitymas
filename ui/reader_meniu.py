# reader_meniu.py

from utils.helper_functions import _input_text, _ask_choice

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
            pass

        elif selection == "5":
            pass

        elif selection == "9":
            return
