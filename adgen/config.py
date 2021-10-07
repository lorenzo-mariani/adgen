import time
from adgen.utils.utils import get_list_from_pkl, get_list_from_default_ini

DEFAULT_CONFIG = {
    'url': 'bolt://localhost:7687',
    'username': 'neo4j',
    'password': 'neo4jj',
    'driver': None,
    'connected': False,
    'nodes': 500,
    'domain': 'TESTLAB.LOCAL',
    'current_time': int(time.time()),
    'sid': 'S-1-5-21-883232822-274137685-4173207997',
    'first_names': get_list_from_pkl("first.pkl"),
    'last_names': get_list_from_pkl("last.pkl"),
    'clients_os': get_list_from_default_ini("CLIENTS"),
    'servers_os': get_list_from_default_ini("SERVERS"),
    'acls': get_list_from_default_ini("ACLS"),
    'groups': get_list_from_default_ini("GROUPS"),
    'ous': get_list_from_default_ini("OUS")
}
