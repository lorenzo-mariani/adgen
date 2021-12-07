import random
import itertools
import math


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
        size     -- where to stop in the iteration
    """
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


def get_fixed_generation(num_nodes, generic_list):
    """
    This function allows you to have a fixed generation
    of nodes, i.e., the number of nodes in the specified
    list will not be approximately equal to the percentage
    indicated in the .ini configuration file but will be
    exactly equal to the percentage.

    Arguments:
        num_nodes    -- number of nodes to generate
        generic_list -- list of which you want to have a
                        fixed generation

    Returns:
        A list containing for each "entry" the exact number
        of nodes to be generated
    """
    dictionary = {}

    tmp_string = generic_list[0]
    tmp_value = 1

    for i in range(1, len(generic_list)):
        if generic_list[i] == tmp_string:
            tmp_value += 1
        else:
            dictionary[tmp_string] = tmp_value
            tmp_string = generic_list[i]
            tmp_value = 1

    dictionary[tmp_string] = tmp_value

    remaining_nodes = num_nodes

    for k in dictionary.keys():
        percentage = math.floor((num_nodes * dictionary.get(k)) / 100)
        dictionary[k] = percentage
        remaining_nodes -= percentage

    if remaining_nodes != 0:
        dictionary[list(dictionary.keys())[-1]] = dictionary.get(list(dictionary.keys())[-1]) + remaining_nodes
        remaining_nodes -= remaining_nodes

    result = []

    for k in dictionary.keys():
        value = dictionary.get(k)
        for i in range(value):
            result.append(k)

    return result
