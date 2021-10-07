from adgen.initializer import initialize
from adgen.db import connect, generate


def config(args):
    config_entity = initialize(args)

    connect(config_entity)
    generate(config_entity)
