import yaml
import os.path

from adgen.initializer import initialize
from adgen.db import clear_and_generate
from adgen.utils.loader import check_parameters


def check_config_args(args):
    """
    This function checks whether the user has entered --nodes-distr
    or not and, if it is, it checks if the inserted path exists and
    if there are valid distributions inside it.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    if not os.path.exists(args.get('conn')):
        raise Exception(f"ERROR: Reading From File: file {args.get('conn')} does not exist")

    if not os.path.exists(args.get('param')):
        raise Exception(f"ERROR: Reading From File: file {args.get('param')} does not exist")

    if args.get('nodes_distr') is not None:
        path_to_check = args.get('nodes_distr')

        # Check if the specified file exists
        if not os.path.exists(path_to_check):
            raise Exception(f"ERROR: Reading From File: file {path_to_check} does not exist")

        with open(path_to_check) as fh:
            data = yaml.load(fh, Loader=yaml.FullLoader)

            # Check if only one distribution is enabled
            if data is None:
                raise Exception(f"ERROR: Reading From File: no distribution enabled")
            elif len(data) > 1:
                raise Exception(f"ERROR: Reading From File: more than one distribution enabled")

            correct_keys = ['distribution', 'x', 'y']
            data_keys = data[0].keys()

            # Check if there are the correct keys inside the file
            for key in data_keys:
                if key not in correct_keys:
                    raise Exception(f"Error: Reading From File: wrong {key} key. Check that only the keys 'distribution', 'x' and 'y' are present")

            # Check if the enabled distribution is valid
            available_distr = ['uniform', 'triangular', 'gauss', 'normal']
            distr = data[0].get('distribution').lower()
            if distr not in available_distr:
                raise Exception("Error: Reading From File: distribution not available. Available distributions are: uniform, triangular, gauss, normal")


def config(args):
    """
    This function executes the config mode.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    path_to_check = args.get('param')
    check = check_parameters(path_to_check)

    if check == 0:
        db_settings, domain_settings, pool = initialize(args)
        clear_and_generate(db_settings, domain_settings, pool)
    elif check == -1:
        raise Exception(f"Reading from File: {path_to_check} seems to return incorrect sections")
    elif check == -2:
        raise Exception(f"Reading from File: {path_to_check} seems to return wrong values of a section")
