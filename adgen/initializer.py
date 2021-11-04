from adgen.default_config import DEFAULT_DB_SETTINGS, DEFAULT_DOMAIN_SETTINGS, DEFAULT_POOL
from adgen.entities.db_settings import DbSettings
from adgen.entities.domain_settings import DomainSettings
from adgen.entities.pool import Pool
from adgen.utils.loader import get_list_from_ini, get_value_from_ini


def initialize(args):
    """
    Initialize some entities with the provided configuration.

    Arguments:
        args -- the list of arguments passed from the command line

    Returns:
        db_settings     -- an entity containing URL, username,
                           password, driver, and connected, i.e.,
                           parameters useful for the connection to
                           the database
        domain_settings -- an entity containing nodes, domain,
                           current_time and sid of the domain to generate
        pool            -- an entity containing a pool of values
                           used to create nodes inside the domain,
                           i.e., a list of first names and last names,
                           a list of client OS and server OS, a list
                           of acls, groups, and ous
    """
    db_settings = DbSettings()
    domain_settings = DomainSettings()
    pool = Pool()

    domain_settings.current_time = DEFAULT_DOMAIN_SETTINGS.get('current_time')
    domain_settings.sid = DEFAULT_DOMAIN_SETTINGS.get('sid')
    pool.first_names = DEFAULT_POOL.get('first_names')
    pool.last_names = DEFAULT_POOL.get('last_names')

    if args.get('command') == "config":
        try:
            db_settings.url = get_value_from_ini("CONNECTION", "url", args.get('conn'))
            db_settings.username = get_value_from_ini("CONNECTION", "username", args.get('conn'))
            db_settings.password = get_value_from_ini("CONNECTION", "password", args.get('conn'))
            domain_settings.domain = get_value_from_ini("CONNECTION", "domain", args.get('conn'))
            domain_settings.nodes = get_value_from_ini("CONNECTION", "nodes", args.get('conn'))
            pool.clients_os = get_list_from_ini("CLIENTS", args.get('param'))
            pool.servers_os = get_list_from_ini("SERVERS", args.get('param'))
            pool.acls = get_list_from_ini("ACLS", args.get('param'))
            pool.groups = get_list_from_ini("GROUPS", args.get('param'))
            pool.ous = get_list_from_ini("OUS", args.get('param'))

        except Exception as err:
            print("Failed Retrieving Data: {error}".format(error=err))
    else:
        pool.clients_os = DEFAULT_POOL.get('clients_os')
        pool.servers_os = DEFAULT_POOL.get('servers_os')
        pool.acls = DEFAULT_POOL.get('acls')
        pool.groups = DEFAULT_POOL.get('groups')
        pool.ous = DEFAULT_POOL.get('ous')

        if args.get('command') == "run":
            db_settings.url = args.get('url')
            db_settings.username = args.get('user')
            db_settings.password = args.get('passwd')
            domain_settings.nodes = args.get('nodes')
            domain_settings.domain = args.get('domain').upper()

        elif args.get('command') == "interactive":
            db_settings.url = DEFAULT_DB_SETTINGS.get('url')
            db_settings.username = DEFAULT_DB_SETTINGS.get('username')
            db_settings.password = DEFAULT_DB_SETTINGS.get('password')
            domain_settings.nodes = DEFAULT_DOMAIN_SETTINGS.get('nodes')
            domain_settings.domain = DEFAULT_DOMAIN_SETTINGS.get('domain')

    return db_settings, domain_settings, pool
