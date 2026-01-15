import datetime as dt
from uuid import UUID
import random

from models.book import Book
from models.reader import Reader
from models.librarian import Librarian

class Library:
    def __init__(self):
        self.books = {}                 
        self.loans = {}                 
        self.readers = {}               
        self.librarians = {}            

    # ----- Registracija / auth -----

    def add_librarian(self, user_name, password):
        if user_name in self.librarians:
            raise ValueError("Toks bibliotekininkas jau egzistuoja.")
        new_librarian = Librarian(user_name, password)
        self.librarians[user_name] = new_librarian
        return new_librarian
    

    def authenticate_librarian(self, user_name, password):
        libr = self.librarians.get(user_name)
        if libr and libr.password == password:
            return libr
        return None
    
    
    def register_reader(self, name, last_name, password):
        if not name.strip() or not last_name.strip():
            raise ValueError("Vardas ir pavardė negali būti tušti.")

        card_id = self._generate_reader_card_id(name.strip(), last_name.strip())
        reader = Reader(name.strip(), last_name.strip(), card_id, password)
        self.readers[card_id] = reader
        return reader
    

    def authenticate_reader(self, card_id, password):
        reader = self.readers.get(card_id)
        if reader and reader.password == password:
            return reader
        return None
    
    
    def _generate_reader_card_id(self, name, last_name):
        initials = (name[:1] + last_name[:1]).upper()
        while True:
            digits = str(random.randint(0, 999999)).zfill(6)
            card_id = f"{initials}-{digits}"
            if card_id not in self.readers:
                return card_id


    # Turėtų būti galimybė ieškoti knygų bibliotekoje, pagal knygos pavadinimą arba autorių.
    def book_search(self):
        pass

    # Turėtų būti galimybė išvesti statistiką, koks yra vidutinis vėluojančių knygų kiekis ir kitus aktualius rodiklius, tokius kaip, kokio žanro knygų yra daugiausiai, 
    # kokio žanro knygas, dažniausiai ima skaitytojai ir t.t
    def library_statistics(self):
        pass

    def overdue_book_warning(self):
        pass