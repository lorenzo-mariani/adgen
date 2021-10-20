import time
import os
from adgen.utils.utils import get_list_from_pkl, get_list_from_ini

# default_path = os.path.abspath("adgen\\data\\default_config.ini")
default_path = os.path.join(os.path.abspath('adgen'), 'data', 'default_config.ini')

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
    'clients_os': get_list_from_ini("CLIENTS", default_path),
    'servers_os': get_list_from_ini("SERVERS", default_path),
    'acls': get_list_from_ini("ACLS", default_path),
    'groups': get_list_from_ini("GROUPS", default_path),
    'ous': get_list_from_ini("OUS", default_path)
}
