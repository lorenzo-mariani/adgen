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
    """
    Prompts you to enter parameters from the command line.

    Arguments:
    prompt  -- the message to prompt
    default -- the default value to use if you do not want to change the parameter
    """
    return input("%s [%s] " % (prompt, default)) or default


def help():
    """Print help messages."""
    print_help()


def dbconfig(entity):
    """
    This function allows you to configure the URL, username
    and password of an entity.

    Arguments:
    entity -- the entity to which to configure the URL, username and password
    """
    print("Current settings:")
    print_db_settings(entity.url, entity.username, entity.password)
    entity.url = input_default("Enter DB URL", entity.url)
    entity.username = input_default("Enter DB Username", entity.username)
    entity.password = input_default("Enter DB Password", entity.password)
    print("\nNew Settings:")
    print_db_settings(entity.url, entity.username, entity.password)
    print("Testing DB Connection")
    connect(entity)


def setnodes(entity):
    """
    This function allows you to configure the nodes of an entity.

    Arguments:
    entity -- the entity to which to configure the nodes
    """
    entity.nodes = int(input_default("Number of nodes of each type to generate", entity.nodes))


def setdomain(entity):
    """
    This function allows you to configure the domain of an entity.

    Arguments:
    entity -- the entity to which to configure the domain
    """
    entity.domain = input_default("Domain", entity.domain).upper()
    print("\nNew Settings:")
    print("Domain: {}".format(entity.domain))


def exit():
    """Exits the program."""
    sys.exit(1)


def connect(entity):
    """
    Connects to the database.

    Arguments:
    entity -- the entity used to connect to the database
    """
    test_db_connection(entity)
    print("Database Connection Successful!")


def cleardb(entity, args):
    """
    Clears the database.

    Arguments:
    entity -- the entity containing information about the database
              connection
    args   -- the information about the current session
    """
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
    """
    Tests the database connection.

    Arguments:
    entity -- the entity used to connect to the database
    """
    entity.connected = False
    if entity.driver is not None:
        entity.driver.close()
    try:
        entity.driver = GraphDatabase.driver(entity.url, auth=(entity.username, entity.password))
        entity.connected = True
    except Exception as err:
        entity.connected = False
        print("Connection Failed: {error}".format(error=err))


def clear_and_generate(entity):
    """
    Clears the database and generates random data.

    Arguments:
    entity -- the entity containing information about the database
              connection and the parameters to be used for data
              generation
    """
    connect(entity)
    cleardb(entity, "a")
    generate_data(entity)


def generate_data(entity):
    """
    Generates random data.

    Arguments:
    entity -- the entity containing information about the
              parameters to be used for data generation
    """
    if not entity.connected:
        print("Not connected to the database")
        return

    computers = []
    groups = []
    users = []
    gpos = []
    ou_guid_map = {}
    ou_props = []

    session = entity.driver.session()

    print("Starting data generation with nodes={}".format(entity.nodes))
    data_generation(session, entity.domain, entity.sid)

    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())
    dcou = str(uuid.uuid4())

    create_default_gpos(session, entity.domain, ddp, ddcp)
    create_dcs_ous(session, entity.domain, dcou)

    print("Adding Standard Edges")
    add_standard_edges(session, entity.domain, dcou)

    print("Generating Computer Nodes")
    computers_props, computers, ridcount = create_computers(session, entity.domain, entity.sid, entity.nodes, computers, entity.clients_os)

    print("Creating Domain Controllers")
    dcs_props, ridcount = create_dcs(session, entity.domain, entity.sid, dcou, ridcount, entity.servers_os, entity.ous)

    print("Generating User Nodes")
    user_props, users, ridcount = create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)

    print("Generating Group Nodes")
    groups_props, groups, ridcount = create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount, entity.groups)

    print("Adding Domain Admins to Local Admins of Computers")
    add_domain_admin_to_local_admin(session, entity.sid)

    das = add_domain_admins(session, entity.domain, entity.nodes, users)

    print("Applying random group nesting")
    create_nested_groups(session, entity.nodes, groups)

    print("Adding users to groups")
    it_users = add_users_to_group(session, entity.nodes, users, groups, das, entity.groups)

    print("Adding local admin rights")
    it_groups = add_local_admin_rights(session, groups, computers)

    print("Adding RDP/ExecuteDCOM/AllowedToDelegateTo")
    add_rdp_dcom_delegate(session, computers, it_users, it_groups)

    print("Adding sessions")
    add_sessions(session, entity.nodes, computers, users, das)

    print("Adding Domain Admin ACEs")
    add_domain_admin_aces(session, entity.domain, computers, users, groups)

    print("Creating OUs")
    ou_props, ou_guid_map = create_computers_ous(session, entity.domain, computers, ou_guid_map, ou_props, entity.nodes, entity.ous)
    ou_props, ou_guid_map = create_users_ous(session, entity.domain, users, ou_guid_map, ou_props, entity.nodes, entity.ous)
    link_ous_to_domain(session, entity.domain, ou_guid_map)

    print("Creating GPOs")
    gpos = create_gpos(session, entity.domain, gpos)
    link_to_ous(session, gpos, entity.domain, ou_guid_map)
    add_outbound_acls(session, it_groups, it_users, gpos, computers, entity.acls)

    print("Marking some users as Kerberoastable")
    add_kerberoastable_users(session, it_users)

    print("Adding unconstrained delegation to a few computers")
    add_unconstrained_delegation(session, computers)

    session.run("MATCH (n:User) SET n.owned=false")
    session.run("MATCH (n:Computer) SET n.owned=false")
    session.run("MATCH (n) SET n.domain=$domain", domain=entity.domain)

    session.close()

    print("Database Generation Finished!")
