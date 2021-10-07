from adgen.config import DEFAULT_CONFIG
from adgen.entities.entity import Entity
from adgen.utils.utils import get_list_from_ini, get_value_from_ini


def initialize(args):
    ent = Entity()
    ent.current_time = DEFAULT_CONFIG.get('current_time')
    ent.sid = DEFAULT_CONFIG.get('sid')
    ent.first_names = DEFAULT_CONFIG.get('first_names')
    ent.last_names = DEFAULT_CONFIG.get('last_names')
    ent.acls = DEFAULT_CONFIG.get('acls')
    ent.groups = DEFAULT_CONFIG.get('groups')
    ent.ous = DEFAULT_CONFIG.get('ous')

    if args.get('command') == "config":
        try:
            ent.url = get_value_from_ini("CONNECTION", "url", args.get('conn'))
            ent.username = get_value_from_ini("CONNECTION", "username", args.get('conn'))
            ent.password = get_value_from_ini("CONNECTION", "password", args.get('conn'))
            ent.domain = get_value_from_ini("CONNECTION", "domain", args.get('conn'))
            ent.nodes = get_value_from_ini("CONNECTION", "nodes", args.get('conn'))
            ent.clients_os = get_list_from_ini("CLIENTS", args.get('os'))
            ent.servers_os = get_list_from_ini("SERVERS", args.get('os'))
        except Exception as err:
            print("Failed Retrieving Data: {error}".format(error=err))
    else:
        ent.clients_os = DEFAULT_CONFIG.get('clients_os')
        ent.servers_os = DEFAULT_CONFIG.get('servers_os')

        if args.get('command') == "run":
            ent.url = args.get('url')
            ent.username = args.get('user')
            ent.password = args.get('passwd')
            ent.nodes = args.get('nodes')
            ent.domain = args.get('domain').upper()

        elif args.get('command') == "interactive":
            ent.url = DEFAULT_CONFIG.get('url')
            ent.username = DEFAULT_CONFIG.get('username')
            ent.password = DEFAULT_CONFIG.get('password')
            ent.nodes = DEFAULT_CONFIG.get('nodes')
            ent.domain = DEFAULT_CONFIG.get('domain')

    return ent
