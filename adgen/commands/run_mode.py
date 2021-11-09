import os

from adgen.initializer import initialize
from adgen.db import clear_and_generate
from adgen.utils.loader import check_parameters


def check_args(args):
    """
    This function checks whether the user has entered --nodes-val or
    --nodes-distr and, in the latter case, checks whether the inserted
    distribution is valid.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    if args.get('nodes_val') is None and args.get('nodes_distr') is None:
        raise Exception("Missing nodes option. You can either use --nodes-val or -nodes-distr")
    elif args.get('nodes_val') is not None and args.get('nodes_distr') is not None:
        raise Exception("You cannot use both --nodes-val and --nodes-distr at the same time. You only have to use one of them")

    if args.get('nodes_distr') is not None:
        available_distr = ['uniform', 'triangular', 'gauss', 'normal']

        txt = args.get('nodes_distr').split("(")
        distr = txt[0].lower()

        if distr not in available_distr:
            raise Exception(f"Distribution {distr} does not exist. Choose from:"
                            f"\n\t- uniform(a,b)"
                            f"\n\t- triangular(low,high)"
                            f"\n\t- gauss(mu,sigma)"
                            f"\n\t- normal(mu,sigma)")


def run(args):
    """
    This function executes the run mode.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    path_to_check = os.path.join(os.path.abspath('adgen'), 'data', 'default_config.ini')
    check = check_parameters(path_to_check)

    if check == 0:
        db_settings, domain_settings, pool = initialize(args)
        clear_and_generate(db_settings, domain_settings, pool)
    elif check == -1:
        raise Exception(f"Reading from File: {path_to_check} seems to return incorrect sections")
    elif check == -2:
        raise Exception(f"Reading from File: {path_to_check} seems to return wrong values of a section")
