from adgen.config import DEFAULT_CONFIG


def initialize(entity, mode):
    if mode == "interactive":
        entity.url = DEFAULT_CONFIG.get('url')
        entity.username = DEFAULT_CONFIG.get('username')
        entity.password = DEFAULT_CONFIG.get('password')
        entity.nodes = DEFAULT_CONFIG.get('nodes')
        entity.domain = DEFAULT_CONFIG.get('domain')
        entity.current_time = DEFAULT_CONFIG.get('current_time')
        entity.sid = DEFAULT_CONFIG.get('sid')
        entity.first_names = DEFAULT_CONFIG.get('first_names')
        entity.last_names = DEFAULT_CONFIG.get('last_names')

    elif mode == "run":
        entity.current_time = DEFAULT_CONFIG.get('current_time')
        entity.sid = DEFAULT_CONFIG.get('sid')
        entity.first_names = DEFAULT_CONFIG.get('first_names')
        entity.last_names = DEFAULT_CONFIG.get('last_names')
