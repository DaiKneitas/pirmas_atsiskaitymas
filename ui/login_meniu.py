# login_meniu.py

from utils.helper_functions import _ask_choice, _input_text, _clear_screen

def login_meniu(library, save):
    last_message = ""

    while True:
        _clear_screen()

        if last_message:
            print(last_message)
            print()

        selection = _ask_choice("""
--------------------------------------------
Prisijungimas:
--------------------------------------------
1) Bibliotekininkas
2) Skaitytojas

--------------------------------------------
Registracija naujiems programos vartotojams
--------------------------------------------
3) Sukurti bibliotekininko paskyrą
4) Sukurti skaitytojo paskyrą

--------------------------------------------
9) Išeiti
--------------------------------------------
""", {"1","2","3","4","9"})

        if selection == "1":
            print("--- Bibliotekininko prisijungimas ---")
            user_name = _input_text("Įveskite savo prisijungimo vardą: ")
            password = _input_text("Įveskite savo slaptažodį: ")

            librarian = library.authenticate_librarian(user_name, password)
            if librarian:
                return ("librarian", librarian)

            last_message = "☠️❌ Neteisingai suvesti bibliotekininko prisijungimo duomenys!"

        elif selection == "2":
            print("--- Skaitytojo prisijungimas ---")
            card_id = _input_text("Įveskite savo kortelės numerį: ")
            password = _input_text("Įveskite savo slaptažodį: ")

            reader = library.authenticate_reader(card_id, password)
            if reader:
                return ("reader", reader)

            last_message = "☠️❌ Neteisingai suvesti skaitytojo prisijungimo duomenys!"

        elif selection == "3":
            print("--- Bibliotekininko registracija ---")
            user_name = _input_text("Įveskite norimą prisijungimo vardą: ")
            password = _input_text("Įveskite norimą slaptažodį: ")

            try:
                library.add_librarian(user_name, password)
                save()
                last_message = "✅ Bibliotekininkas sukurtas. Dabar prisijunkite."
            except Exception as e:
                last_message = f"☠️❌ Klaida: {e}"

        elif selection == "4":
            print("--- Skaitytojo registracija ---")
            name = _input_text("Įveskite savo vardą: ")
            last_name = _input_text("Įveskite savo pavardę: ")
            password = _input_text("Įveskite norimą slaptažodį: ")

            try:
                reader = library.register_reader(name, last_name, password)
                save()

                print(f"\n✅ Skaitytojas sukurtas! Jūsų kortelės numeris: {reader.reader_card_id}")
                input("Spauskite Enter, kad grįžti į prisijungimo meniu...")

                last_message = "✅ Registracija sėkminga. Prisijunkite su kortelės numeriu."
                continue

            except Exception as e:
                last_message = f"☠️❌ Klaida: {e}"

        elif selection == "9":
            return None



