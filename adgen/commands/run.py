from adgen.initializer import initialize
from adgen.db import connect, generate


def run(args):
    """
    This function executes the run mode.

    Arguments:
    args -- the list of arguments passed from the command line
    """
    run_entity = initialize(args)

    connect(run_entity)
    generate(run_entity)
