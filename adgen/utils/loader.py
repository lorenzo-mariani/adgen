import os
import pickle

from configparser import ConfigParser


def get_list_from_pkl(args):
    """
    Retrieve a list inside a .pkl file.

    Arguments:
        args -- the name of the .pkl file

    Returns:
        The list inside the .pkl file
    """
    path = os.path.join(os.path.abspath('adgen'), 'data', args)

    with open(path, "rb") as f:
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


def check_ini_file(path):
    """
    This function performs checks on the sections within a .ini file.
        - It checks if all the sections are present correctly
        - Since the values of the options in a section represent
          the probability of having that detarminate option, it checks
          whether the sum of the values is equal to 100%

    Arguments:
        path -- the name of the .ini file

    Returns:
         0 -- everything is ok
        -1 -- sections are incorrect
        -2 -- the sum of the options in a section is not
              equal to 100 or there is a value lower than 0
    """
    config = ConfigParser()
    config.optionxform = str

    if not config.read(path):
        raise Exception(f"Reading from File: {path} seems to return and empty object")
    else:
        config.read(path)

    sections_found = config.sections()
    sections_found.sort()

    sections_to_have = ['CLIENTS', 'SERVERS', 'ACLS', 'GROUPS', 'OUS']
    sections_to_have.sort()

    if sections_found != sections_to_have:
        return -1

    sections_found.remove('OUS')

    for section in sections_found:
        sum = 0

        for opt in config.options(section):
            if config.getint(section, opt) < 0:
                return -2
            sum += config.getint(section, opt)

        if sum != 100:
            return -2

    return 0
