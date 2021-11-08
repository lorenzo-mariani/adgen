def print_commands():
    """Prints the commands available in interactive mode."""
    print(
        """
=========================================================
                    CHOOSE A COMMAND:

  1 - [clear_and_generate]          6  - [generate]
  2 - [cleardb]                     7  - [help]
  3 - [connect]                     8  - [setdomain]
  4 - [dbconfig]                    9  - [setnodes]
  5 - [exit]                        10 - [setnodes_distr]
=========================================================
    """
    )


def print_help():
    """
    Prints the help messages of each command available
    in interactive mode.
    """
    print("\n[clear_and_generate]" + "\t" * 2 + "Connect to the database, clear the db, set the schema, and generate random data")
    print("[cleardb]" + "\t" * 3 + "Clear the database and set constraints")
    print("[connect]" + "\t" * 3 + "Test connection to the database and verify credentials")
    print("[dbconfig]" + "\t" * 3 + "Configure database connection parameters")
    print("[exit]" + "\t" * 4 + "Exits the database creator")
    print("[generate]" + "\t" * 3 + "Generate random data")
    print("[help]" + "\t" * 4 + "Shows a brief description of the various commands (type help <topic>)")
    print("[setdomain]" + "\t" * 3 + "Set domain name (default 'TESTLAB.LOCAL')")
    print("[setnodes]" + "\t" * 3 + "Set base number of nodes to generate (default 600)")
    print("[setnodes_distr]" + "\t" * 2 + "Set nodes distribution\n")


def print_db_settings(url, username, password):
    """
    Prints the URL, username and password of the database.

    Arguments:
        url      -- The URL of the database
        username -- The username of the database
        password -- The password of the database
    """
    print("DB Url: {}".format(url))
    print("DB Username: {}".format(username))
    print("DB Password: {}".format(password))
    print("")
