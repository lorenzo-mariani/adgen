import sys

from adgen.cl_parser import parse_args
from adgen.commands.interactive_mode import interactive
from adgen.commands.run_mode import run, check_run_args
from adgen.commands.config_mode import config, check_config_args


def main():
    """ Main routine of adgen """
    args = parse_args(sys.argv[1:])
    cmd = args.command
    cmd_params = vars(args)

    try:
        if cmd == "interactive":
            interactive(cmd_params)
        elif cmd == "run":
            check_run_args(cmd_params)
            run(cmd_params)
        elif cmd == "config":
            check_config_args(cmd_params)
            config(cmd_params)
    except Exception as err:
        print("{error}".format(error=err))
