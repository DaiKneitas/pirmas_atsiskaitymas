import pickle

def read_file(file_name):
    with open(file_name) as f:
        return pickle.load(f)