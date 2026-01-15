import uuid

class Book:
    def __init__(self, name, author, year, genre):
        self.id = uuid.uuid4()
        self.name = name
        self.author = author
        self.year = year
        self.genre = genre

    def __str__(self):
        return f"{self.name} — {self.author} ({self.year}) [{self.genre}]"

