import os

from adgen.db import help, dbconfig, exit, connect, cleardb, setnodes, setdomain, clear_and_generate, generate_data
from adgen.initializer import initialize
from adgen.utils.printer import print_commands
from adgen.utils.loader import check_parameters


def interactive(args):
    """
    This function executes the interactive mode.

    Arguments:
        args -- the list of arguments passed from the command line
    """
    path_to_check = os.path.join(os.path.abspath('adgen'), 'data', 'default_config.ini')
    check = check_parameters(path_to_check)
    if check == 0:
        interactive_entity = initialize(args)

        while True:
            print_commands()
            print("[cmd] ")
            command = input()

            try:
                if command == "help":
                    help()
                elif command == "dbconfig":
                    dbconfig(interactive_entity)
                elif command == "exit":
                    exit()
                elif command == "connect":
                    connect(interactive_entity)
                elif command == "cleardb":
                    cleardb(interactive_entity, "a")
                elif command == "setnodes":
                    setnodes(interactive_entity)
                elif command == "setdomain":
                    setdomain(interactive_entity)
                elif command == "clear_and_generate":
                    clear_and_generate(interactive_entity)
                elif command == "generate":
                    generate_data(interactive_entity)
                else:
                    print(command + " does not exist!\n")
            except KeyboardInterrupt:
                if interactive_entity.driver is not None:
                    interactive_entity.driver.close()
                raise KeyboardInterrupt
    elif check == -1:
        raise Exception(f"Reading from File: {path_to_check} seems to return incorrect sections")
    elif check == -2:
        raise Exception(f"Reading from File: {path_to_check} seems to return wrong values of a section")