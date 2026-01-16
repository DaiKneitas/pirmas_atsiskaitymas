import pickle, os

def save_file(file_name, content):
    with open(file_name, "wb") as f:
        pickle.dump(content, f)


def load_file(file_name):
    if not os.path.exists(file_name):
        return None
    with open(file_name, "rb") as f:
        return pickle.load(f)