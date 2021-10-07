from adgen.initializer import initialize
from adgen.db import connect, generate


def run(args):
    run_entity = initialize(args)

    connect(run_entity)
    generate(run_entity)
