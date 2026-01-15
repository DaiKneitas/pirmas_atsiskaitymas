class Reader:
    def __init__(self, name, last_name, reader_card_id, password):
        self.name = name
        self.last_name = last_name
        self.reader_card_id = reader_card_id
        self.password = password
        self.taken_book_ids = []

    def __str__(self):
        return f"{self.name} {self.last_name} (kortelė: {self.reader_card_id})"
