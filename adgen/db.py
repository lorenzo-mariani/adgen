import sys
import uuid

from neo4j import GraphDatabase
from adgen.generators.acls import add_standard_edges, add_domain_admin_to_local_admin, add_local_admin_rights, \
     add_domain_admin_aces, add_outbound_acls
from adgen.generators.computers import create_computers, create_dcs, add_rdp_dcom_delegate, add_sessions, \
     add_unconstrained_delegation
from adgen.generators.gpos import create_default_gpos, create_gpos, link_to_ous
from adgen.generators.groups import data_generation, create_groups, add_domain_admins, create_nested_groups, \
     add_users_to_group
from adgen.generators.ous import create_dcs_ous, create_computers_ous, create_users_ous, link_ous_to_domain
from adgen.generators.users import create_users, add_kerberoastable_users
from adgen.utils.printer import print_help, print_db_settings


def input_default(prompt, default):
    return input("%s [%s] " % (prompt, default)) or default


def help():
    print_help()


def dbconfig(entity):
    print("Current settings:")
    print_db_settings(entity.url, entity.username, entity.password)
    entity.url = input_default("Enter DB URL", entity.url)
    entity.username = input_default("Enter DB Username", entity.username)
    entity.password = input_default("Enter DB Password", entity.password)
    print("\nNew Settings:")
    print_db_settings(entity.url, entity.username, entity.password)
    print("Testing DB Connection")
    test_db_connection(entity)


def setnodes(entity):
    entity.nodes = int(input_default("Number of nodes of each type to generate", entity.nodes))


def setdomain(entity):
    entity.domain = input_default("Domain", entity.domain).upper()
    print("\nNew Settings:")
    print("Domain: {}".format(entity.domain))


def exit():
    sys.exit(1)


def connect(entity):
    test_db_connection(entity)


def cleardb(entity, args):
    if not entity.connected:
        print("Not connected to database. Use connect first")
        return

    print("Clearing Database")
    d = entity.driver
    session = d.session()

    session.run("match (a) -[r] -> () delete a, r")  # delete all nodes with relationships
    session.run("match (a) delete a")  # delete nodes that have no relationships

    session.close()
    print("DB Cleared and Schema Set")


def test_db_connection(entity):
    entity.connected = False
    if entity.driver is not None:
        entity.driver.close()
    try:
        entity.driver = GraphDatabase.driver(entity.url, auth=(entity.username, entity.password))
        entity.connected = True
        print("Database Connection Successful!")
    except Exception as err:
        entity.connected = False
        print("Connection Failed: {error}".format(error=err))


def generate(entity):
    generate_data(entity)


def clear_and_generate(entity):
    test_db_connection(entity)
    cleardb(entity, "a")
    generate_data(entity)


def generate_data(entity):
    if not entity.connected:
        print("Not connected to the database")
        return

    computers = []
    computers_props = []
    dcs_props = []
    groups = []
    groups_props = []
    users = []
    user_props = []
    gpos = []
    ou_guid_map = {}
    ou_props = []

    session = entity.driver.session()

    data_generation(session, entity.domain, entity.sid, entity.nodes)

    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())
    dcou = str(uuid.uuid4())

    create_default_gpos(session, entity.domain, ddp, ddcp)
    create_dcs_ous(session, entity.domain, dcou)
    add_standard_edges(session, entity.domain, dcou)

    computers_props, computers, ridcount = create_computers(session, entity.domain, entity.sid, entity.nodes, computers)
    dcs_props, ridcount = create_dcs(session, entity.domain, entity.sid, dcou, ridcount)
    user_props, users, ridcount = create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    groups_props, groups, ridcount = create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount)

    add_domain_admin_to_local_admin(session, entity.sid)

    das = add_domain_admins(session, entity.domain, entity.nodes, users)

    create_nested_groups(session, entity.nodes, groups)

    it_users = add_users_to_group(session, entity.nodes, users, groups, das)
    it_groups = add_local_admin_rights(session, groups, computers)

    add_rdp_dcom_delegate(session, computers, it_users, it_groups)
    add_sessions(session, entity.nodes, computers, users, das)
    add_domain_admin_aces(session, entity.domain, computers, users, groups)

    ou_props, ou_guid_map = create_computers_ous(session, entity.domain, computers, ou_guid_map, ou_props, entity.nodes)
    ou_props, ou_guid_map = create_users_ous(session, entity.domain, users, ou_guid_map, ou_props, entity.nodes)

    link_ous_to_domain(session, entity.domain, ou_guid_map)

    gpos = create_gpos(session, entity.domain, gpos)

    link_to_ous(session, gpos, entity.domain, ou_guid_map)

    add_outbound_acls(session, it_groups, it_users, gpos, computers)
    add_kerberoastable_users(session, it_users)
    add_unconstrained_delegation(session, computers)

    session.run("MATCH (n:User) SET n.owned=false")
    session.run("MATCH (n:Computer) SET n.owned=false")
    session.run("MATCH (n) SET n.domain=$domain", domain=entity.domain)

    session.close()

    print("Database Generation Finished!")
