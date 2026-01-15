# Pagalbine funkcija vartotojo input patikrai, kad nebutu paliktas tuscias laukas
def _input_text(text_for_user, min_length=1):
    while True:
        user_input = input(text_for_user)
        if len(user_input) >= min_length:
            return user_input
        
        print("Laukas negali būti tuščias, įveskite reikiamą tekstą")


# Pagalbine funkcija meniu patikrai, kad būtų įvestas tik leidžiamas pasirinkimas iš sarašo
def _ask_choice(prompt, allowed):
    while True:
        user_input = input(prompt).strip()
        if user_input in allowed:
            return user_input
        print("Neteisinga įvestis.")