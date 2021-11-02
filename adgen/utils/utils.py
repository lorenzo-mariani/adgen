import random
import itertools


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
