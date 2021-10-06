import os
import pickle


def get_path():
    data_path = "\\Desktop\\ADGenerator\\ADGenerator\\data\\"
    return os.path.expanduser("~") + data_path


def get_first_names():
    with open(get_path() + "first.pkl", "rb") as f:
        return pickle.load(f)


def get_last_names():
    with open(get_path() + "last.pkl", "rb") as f:
        return pickle.load(f)
