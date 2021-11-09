import argparse
import sys


def parse_args(args):
    """
    This function parses the arguments which have been passed from the command
    line, these can be easily retrieved for example by using "sys.argv[1:]".
    It returns an argparse Namespace object.

    Arguments:
        args -- the list of arguments passed from the command line as the sys.argv format

    Returns:
        An argparse Namespace object with the provided arguments, which
        can be used in a simpler format.
    """
    parser = argparse.ArgumentParser(prog='adgen', description='An Active Directory generator')

    subparsers = parser.add_subparsers(help='commands', dest='command')
    subparsers.required = True

    # Main Commands
    interactive_parser = subparsers.add_parser('interactive', help='interactive mode')
    config_parser = subparsers.add_parser('config', help='configuration mode')
    run_parser = subparsers.add_parser('run', help='run mode')

    # config parser
    config_parser.add_argument('--conn', type=str, required=True, help='absolute path to the file containing the '
                                                                       'parameters necessary for the connection to '
                                                                       'the database, i.e., url, username, password, '
                                                                       'nodes, domain')
    config_parser.add_argument('--param', type=str, required=True, help='absolute path to the file containing the '
                                                                        'list of client/server operating systems ('
                                                                        'along with their frequencies) that adgen '
                                                                        'will use when generating client computers '
                                                                        'and domain controllers, as well as '
                                                                        'information about acls, groups and ous ('
                                                                        'along with their frequencies)')

    # run parser
    run_parser.add_argument('--url', type=str, required=True, help='database URL to connect to')
    run_parser.add_argument('--user', type=str, required=True, help='database Username')
    run_parser.add_argument('--passwd', type=str, required=True, help='database Password')
    run_parser.add_argument('--domain', type=str, required=True, help='name of the domain to generate')
    run_parser.add_argument('--nodes-val', type=int, help='number of nodes to generate')
    run_parser.add_argument('--nodes-distr', type=str, help='distribution of nodes to generate')

    if len(args) == 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    parsed_args = parser.parse_args()
    if parsed_args.command == 'help':
        if not parsed_args.cmd:
            parser.print_help(sys.stderr)
        else:
            try:
                subparsers.choices[parsed_args.cmd].print_help()
            except KeyError:
                print(f'Unknown command name `{parsed_args.cmd}`')
                print(f"Valid commands are: {', '.join(subparsers.choices.keys())}")
        sys.exit(1)

    return parsed_args
