import random
import itertools
import os
import pickle

from configparser import ConfigParser


def cn(name, domain):
    return f"{name}@{domain}"


def cs(rid, sid):
    return f"{sid}-{str(rid)}"


def cws(domain, sid):
    return f"{domain}-{str(sid)}"


def generate_timestamp(current_time):
    choice = random.randint(-1, 1)
    if choice == 1:
        variation = random.randint(0, 31536000)
        return current_time - variation
    else:
        return choice


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


def get_list_from_pkl(args):
    with open(os.path.abspath("adgen\data\\" + args), "rb") as f:
        return pickle.load(f)


def get_list_from_ini(list_name, path):
    config = ConfigParser()
    config.optionxform = str
    config.read(path)

    section = list_name
    generic_list = []

    for opt in config.options(section):
        for frequency in range(0, config.getint(section, opt)):
            generic_list.append(opt)
    return generic_list


def get_value_from_ini(list_name, opt_name, path):
    config = ConfigParser()
    config.optionxform = str
    config.read(path)

    section = list_name

    if opt_name == 'nodes':
        return config.getint(section, opt_name)
    elif opt_name == 'domain':
        return (config.get(section, opt_name)).upper()
    else:
        return config.get(section, opt_name)