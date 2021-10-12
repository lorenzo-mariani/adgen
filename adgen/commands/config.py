from adgen.initializer import initialize
from adgen.db import connect, generate_data


def config(args):
    """
    This function executes the config mode.

    Arguments:
    args -- the list of arguments passed from the command line
    """
    config_entity = initialize(args)

    connect(config_entity)
    generate_data(config_entity)
