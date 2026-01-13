import pickle

def save_file(file_name, content):
    with open(file_name) as f:
        pickle.dump(content, f)