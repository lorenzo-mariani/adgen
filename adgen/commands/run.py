from adgen.entities.entity import Entity
from adgen.initializer import initialize
from adgen.db import connect, generate


def run(args):
    run_entity = Entity()

    run_entity.url = args.get('url')
    run_entity.username = args.get('user')
    run_entity.password = args.get('passwd')
    run_entity.nodes = args.get('nodes')
    run_entity.domain = args.get('domain').upper()

    initialize(run_entity, "run")

    connect(run_entity)
    generate(run_entity)
