import os
import time

from adgen.db import help, dbconfig, exit, connect, cleardb, setnodes, setnodes_distr, setdomain, clear_and_generate,\
     generate_data
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
        db_settings, domain_settings, pool = initialize(args)

        while True:
            print_commands()
            print("[cmd] ")
            command = input()

            try:
                if command == "help":
                    help()
                elif command == "dbconfig":
                    dbconfig(db_settings)
                elif command == "exit":
                    exit()
                elif command == "connect":
                    connect(db_settings)
                elif command == "cleardb":
                    cleardb(db_settings, "a")
                elif command == "setnodes":
                    setnodes(domain_settings)
                elif command == "setnodes_distr":
                    setnodes_distr(domain_settings)
                elif command == "setdomain":
                    setdomain(domain_settings)
                elif command == "clear_and_generate":
                    clear_and_generate(db_settings, domain_settings, pool)
                elif command == "generate":
                    generate_data(db_settings, domain_settings, pool)
                else:
                    print(command + " does not exist!\n")
                time.sleep(0.3)
            except KeyboardInterrupt:
                if db_settings.driver is not None:
                    db_settings.driver.close()
                raise KeyboardInterrupt
    elif check == -1:
        raise Exception(f"Reading from File: {path_to_check} seems to return incorrect sections")
    elif check == -2:
        raise Exception(f"Reading from File: {path_to_check} seems to return wrong values of a section")
