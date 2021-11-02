import os

from adgen.initializer import initialize
from adgen.db import clear_and_generate
from adgen.utils.utils import check_parameters


def run(args):
    """
    This function executes the run mode.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    path_to_check = os.path.join(os.path.abspath('adgen'), 'data', 'default_config.ini')
    check = check_parameters(path_to_check)

    if check == 0:
        run_entity = initialize(args)
        clear_and_generate(run_entity)
    elif check == -1:
        raise Exception(f"Reading from File: {path_to_check} seems to return incorrect sections")
    elif check == -2:
        raise Exception(f"Reading from File: {path_to_check} seems to return wrong values of a section")
