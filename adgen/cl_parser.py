import argparse
import sys


def parse_args(args):
    parser = argparse.ArgumentParser(prog='adgen', description='An Active Directory generator')

    subparsers = parser.add_subparsers(help='commands', dest='command')
    subparsers.required = True

    # Main Commands
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    config_parser = subparsers.add_parser('config', help='Configuration mode')
    run_parser = subparsers.add_parser('run', help='Run mode')

    # config parser
    config_parser.add_argument('--conn', type=str, help='', required=True)
    config_parser.add_argument('--os', type=str, help='', required=True)

    # run parser
    run_parser.add_argument('--url', type=str, help='Database URL to connect to', required=True)
    run_parser.add_argument('--user', type=str, help='Database Username', required=True)
    run_parser.add_argument('--passwd', type=str, help='Database Password', required=True)
    run_parser.add_argument('--nodes', type=int, help='Number of nodes to generate', required=True)
    run_parser.add_argument('--domain', type=str, help='Name of the domain to generate', required=True)

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
                print(
                    f"Valid commands are: {', '.join(subparsers.choices.keys())}"
                )
        sys.exit(1)

    return parsed_args
