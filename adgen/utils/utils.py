import random
import itertools


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


def get_list(list_name, path):
    try:
        pathname = path + str(list_name)
        if pathname:
            list = []
            for key in list_name.keys():
                for freq in range(0, list_name.get(key)):
                    list.append(key)
            return list
    except Exception as err:
        print("Failed Retrieving Data: {error}".format(error=err))
