from adgen.initializer import initialize
from adgen.db import clear_and_generate
from adgen.utils.utils import check_parameters


def config(args):
    """
    This function executes the config mode.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    path_to_check = args.get('param')
    check = check_parameters(path_to_check)

    if check == 0:
        config_entity = initialize(args)
        clear_and_generate(config_entity)
    elif check == -1:
        raise Exception(f"Reading from File: {path_to_check} seems to return incorrect sections")
    elif check == -2:
        raise Exception(f"Reading from File: {path_to_check} seems to return wrong values of a section")
