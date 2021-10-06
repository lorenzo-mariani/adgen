from adgen.db import help, dbconfig, exit, connect, cleardb, setnodes, setdomain, clear_and_generate, generate
from adgen.initializer import initialize
from adgen.entities.entity import Entity
from adgen.utils.printer import print_commands


def interactive():
    interactive_entity = Entity()
    initialize(interactive_entity, "interactive")

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
                generate(interactive_entity)
            else:
                print(command + " does not exist!\n")
        except KeyboardInterrupt:
            if interactive_entity.driver is not None:
                interactive_entity.driver.close()
            raise KeyboardInterrupt
