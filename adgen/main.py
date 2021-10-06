import sys

from adgen.cl_parser import parse_args
from adgen.commands.interactive import interactive
from adgen.commands.run import run


def main():
    """Main routine of adgen."""
    args = parse_args(sys.argv[1:])
    cmd = args.command
    cmd_params = vars(args)

    if cmd == "interactive":
        interactive()
    elif cmd == "run":
        run(cmd_params)

