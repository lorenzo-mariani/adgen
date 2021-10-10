import sys

from adgen.cl_parser import parse_args
from adgen.commands.interactive import interactive
from adgen.commands.run import run
from adgen.commands.config import config


def main():
    """ Main routine of adgen """
    args = parse_args(sys.argv[1:])
    cmd = args.command
    cmd_params = vars(args)

    try:
        if cmd == "interactive":
            interactive(cmd_params)
        elif cmd == "run":
            run(cmd_params)
        elif cmd == "config":
            config(cmd_params)
    except Exception as err:
        print("{error}".format(error=err))
