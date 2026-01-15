from utils.helper_functions import _ask_choice, _input_text


def login_meniu(library):
    while True:
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
""", {"1","2","3","4","9"})

        if selection == "1":
            print("--- Bibliotekininko prisijungimas ---")
            user_name = _input_text("Įveskite savo prisijungimo vardą")
            password = _input_text("Įveskite savo slaptažodį")
            librarian = library.authenticate_librarian(user_name, password)
            if librarian:
                return ("librarian", librarian)  # priskiriama role: "librarian"
            print("Neteisingi prisijungimo duomenys.")

        elif selection == "2":
            print("--- Skaitytojo prisijungimas ---")
            card_id = _input_text("Įveskite kortelės numerį: ")
            password = _input_text("Įveskite slaptažodį: ")

            reader = library.authenticate_reader(card_id, password)
            if reader:
                return ("reader", reader)  # priskiriama role: "reader"
            print("Neteisingi prisijungimo duomenys.")

        elif selection == "3":
            print("--- Bibliotekininko registracija ---")
            user_name = _input_text("Įveskite norimą prisijungimo vardą: ")
            password = _input_text("Įveskite norimą slaptažodį: ")
            try:
                library.add_librarian(user_name, password)
                print("Bibliotekininkas sukurtas.")

                librarian = library.authenticate_librarian(user_name, password)  # auto-login
                return ("librarian", librarian)
            except Exception as e:
                print(f"Klaida: {e}")

        elif selection == "4":
            print("--- Skaitytojo registracija ---")
            name = _input_text("Įveskite savo vardą: ")
            last_name = _input_text("Įveskite savo pavardę: ")
            password = _input_text("Įveskite norimą slaptažodį: ")
            try:
                reader = library.register_reader(name, last_name, password)
                print(f"Skaitytojas sukurtas. Jūsų kortelės numeris: {reader.reader_card_id}")
                return ("reader", reader)  # auto-login
            except Exception as e:
                print(f"Klaida: {e}")

        elif selection == "9":
            return None


