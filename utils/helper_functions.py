# Pagalbine funkcija vartotojo input patikrai, kad nebutu paliktas tuscias laukas
def _input_text(text_for_user, min_length=1):
    while True:
        user_input = input(text_for_user)
        if len(user_input) >= min_length:
            return user_input
        
        print("❌ Laukas negali būti tuščias, įveskite reikiamą tekstą")


# Pagalbine funkcija meniu patikrai, kad būtų įvestas tik leidžiamas pasirinkimas iš sarašo
def _ask_choice(prompt, allowed):
    while True:
        user_input = input(prompt).strip()
        if user_input in allowed:
            return user_input
        print("❌❌❌ --- NETEISINGA ĮVESTIS --- ❌❌❌")


# Pagalbine funkcija, kur patikrina, kad būtų įvestas sveikas skaičius, arba skaičius tam tikrose ribose nuo/iki
def _ask_int(prompt, min_value=None, max_value=None):
    while True:
        skaicius = input(prompt).strip()
        try:
            number = int(skaicius)
        except ValueError:
            print("❌ Įveskite sveiką skaičių.")
            continue

        if min_value is not None and number < min_value:
            print(f"❌ Skaičius per mažas. Turi būti bent {min_value}.")
            continue

        if max_value is not None and number > max_value:
            print(f"❌ Skaičius per didelis. Turi būti ne daugiau {max_value}.")
            continue

        return number

