class Librarian:
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password
    
    def __str__(self):
        return f"Prisijungimo vardas: {self.user_name}"

