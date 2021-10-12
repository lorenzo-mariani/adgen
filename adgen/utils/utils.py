import random
import itertools
import os
import pickle

from configparser import ConfigParser


def cn(name, domain):
    """
    Builds the common name of the element you want to
    create (e.g., computer, gpo, ou, ...).

    Arguments:
        name   -- base name of the element
        domain -- domain name

    Returns:
        The common name of element (e.g., computer01@testlab.local)
    """
    return f"{name}@{domain}"


def cs(rid, sid):
    """
    Creates the cs of an element based on rid.

    Arguments:
        rid -- rid of the element
        sid -- domain sid

    Returns:
        The cs of an element
    """
    return f"{sid}-{str(rid)}"


def cws(domain, sid):
    """
    Creates the cws of an element based on rid.

    Arguments:
        rid -- rid of the element
        sid -- domain sid

    Returns:
        The cws of an element
    """
    return f"{domain}-{str(sid)}"


def generate_timestamp(current_time):
    """
    Creates a timestamp.

    Arguments:
        current_time -- the current time

    Returns:
        The generated timestamp
    """
    choice = random.randint(-1, 1)
    if choice == 1:
        variation = random.randint(0, 31536000)
        return current_time - variation
    else:
        return choice


def split_seq(iterable, size):
    """
    Splits a sequence.

    Arguments:
        iterable -- iterable object
        size -- where to stop in the iteration
    """
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


def get_list_from_pkl(args):
    """
    Retrieve a list inside a .pkl file.

    Arguments:
        args -- the name of the .pkl file

    Returns:
        The list inside the .pkl file
    """
    with open(os.path.abspath("adgen\\data\\" + args), "rb") as f:
        return pickle.load(f)


def get_list_from_ini(list_name, path):
    """
    Retrieve a list inside a .ini file.

    Arguments:
        list_name -- the name of the section to retrieve
        path      -- the name of the .ini file

    Returns:
        The list found, consisting of the options each
        multiplied by the associated value
    """
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
    """
    Retrieve a specific value inside a .ini file.

    Arguments:
        list_name -- the name of the section to retrieve
        opt_name  -- the name of the option to retrieve
        path      -- the name of the .ini file

    Returns:
        The value associated with the specified section and option
    """
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
