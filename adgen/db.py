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


def dbconfig(db_settings):
    """
    This function allows you to configure the URL, username
    and password of an entity.

    Arguments:
        db_settings -- the entity to which to configure the URL,
                       username and password
    """
    print("Current settings:")
    print_db_settings(db_settings.url, db_settings.username, db_settings.password)
    db_settings.url = input_default("Enter DB URL", db_settings.url)
    db_settings.username = input_default("Enter DB Username", db_settings.username)
    db_settings.password = input_default("Enter DB Password", db_settings.password)
    print("\nNew Settings:")
    print_db_settings(db_settings.url, db_settings.username, db_settings.password)
    print("Testing DB Connection")
    connect(db_settings)


def setnodes(domain_settings):
    """
    This function allows you to configure the nodes of an entity.

    Arguments:
        domain_settings -- the entity to which to configure the nodes
    """
    domain_settings.nodes = int(input_default("Number of nodes of each type to generate", domain_settings.nodes))


def setdomain(domain_settings):
    """
    This function allows you to configure the domain of an entity.

    Arguments:
        domain_settings -- the entity to which to configure the domain
    """
    domain_settings.domain = input_default("Domain", domain_settings.domain).upper()
    print("\nNew Settings:")
    print("Domain: {}".format(domain_settings.domain))


def exit():
    """Exits the program."""
    sys.exit(1)


def connect(db_settings):
    """
    Connects to the database.

    Arguments:
        db_settings -- the entity used to connect to the database
    """
    test_db_connection(db_settings)
    print("Database Connection Successful!")


def cleardb(db_settings, args):
    """
    Clears the database.

    Arguments:
        db_settings -- the entity containing information about the
                       database connection
        args        -- the information about the current session
    """
    if not db_settings.connected:
        print("Not connected to database. Use connect first")
        return

    print("Clearing Database")
    session = db_settings.driver.session()

    session.run("match (a) -[r] -> () delete a, r")  # delete all nodes with relationships
    session.run("match (a) delete a")  # delete nodes that have no relationships

    session.close()
    print("DB Cleared and Schema Set")


def test_db_connection(db_settings):
    """
    Tests the database connection.

    Arguments:
        db_settings -- the entity used to connect to the database
    """
    db_settings.connected = False
    if db_settings.driver is not None:
        db_settings.driver.close()
    try:
        db_settings.driver = GraphDatabase.driver(db_settings.url, auth=(db_settings.username, db_settings.password))
        db_settings.connected = True
    except Exception as err:
        db_settings.connected = False
        print("Connection Failed: {error}".format(error=err))


def clear_and_generate(db_settings, domain_settings, pool):  # pragma: no cover
    """
    Clears the database and generates random data.

    Arguments:
        db_settings     -- the entity containing URL, username,
                           password, driver, and connected, i.e.,
                           parameters useful for the connection to
                           the database
        domain_settings -- the entity containing nodes, domain,
                           current_time and sid of the domain to generate
        pool            -- the entity containing a pool of values
                           used to create nodes inside the domain,
                           i.e., a list of first names and last names,
                           a list of client OS and server OS, a list
                           of acls, groups, and ous
    """
    connect(db_settings)
    cleardb(db_settings, "a")
    generate_data(db_settings, domain_settings, pool)


def generate_data(db_settings, domain_settings, pool):  # pragma: no cover
    """
    Generates random data.

    Arguments:
        db_settings     -- the entity containing URL, username,
                           password, driver, and connected, i.e.,
                           parameters useful for the connection to
                           the database
        domain_settings -- the entity containing nodes, domain,
                           current_time and sid of the domain to generate
        pool            -- the entity containing a pool of values
                           used to create nodes inside the domain,
                           i.e., a list of first names and last names,
                           a list of client OS and server OS, a list
                           of acls, groups, and ous
    """
    if not db_settings.connected:
        print("Not connected to the database")
        return

    computers = []
    groups = []
    users = []
    gpos = []
    ou_guid_map = {}
    ou_props = []

    session = db_settings.driver.session()

    print("Starting data generation with nodes={}".format(domain_settings.nodes))
    data_generation(session, domain_settings.domain, domain_settings.sid)

    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())
    dcou = str(uuid.uuid4())

    create_default_gpos(session, domain_settings.domain, ddp, ddcp)
    create_dcs_ous(session, domain_settings.domain, dcou)

    print("Adding Standard Edges")
    add_standard_edges(session, domain_settings.domain, dcou)

    print("Generating Computer Nodes")
    computers_props, computers, ridcount = create_computers(session, domain_settings.domain, domain_settings.sid,
                                                            domain_settings.nodes, computers, pool.clients_os)

    print("Creating Domain Controllers")
    dcs_props, ridcount = create_dcs(session, domain_settings.domain, domain_settings.sid, dcou, ridcount,
                                     pool.servers_os, pool.ous)

    print("Generating User Nodes")
    user_props, users, ridcount = create_users(session, domain_settings.domain, domain_settings.sid,
                                               domain_settings.nodes, domain_settings.current_time, pool.first_names,
                                               pool.last_names, users, ridcount)

    print("Generating Group Nodes")
    groups_props, groups, ridcount = create_groups(session, domain_settings.domain, domain_settings.sid,
                                                   domain_settings.nodes, groups, ridcount, pool.groups)

    print("Adding Domain Admins to Local Admins of Computers")
    add_domain_admin_to_local_admin(session, domain_settings.sid)

    das = add_domain_admins(session, domain_settings.domain, domain_settings.nodes, users)

    print("Applying random group nesting")
    create_nested_groups(session, domain_settings.nodes, groups)

    print("Adding users to groups")
    it_users = add_users_to_group(session, domain_settings.nodes, users, groups, das, pool.groups)

    print("Adding local admin rights")
    it_groups = add_local_admin_rights(session, groups, computers)

    print("Adding RDP/ExecuteDCOM/AllowedToDelegateTo")
    add_rdp_dcom_delegate(session, computers, it_users, it_groups)

    print("Adding sessions")
    add_sessions(session, domain_settings.nodes, computers, users, das)

    print("Adding Domain Admin ACEs")
    add_domain_admin_aces(session, domain_settings.domain, computers, users, groups)

    print("Creating OUs")
    ou_props, ou_guid_map = create_computers_ous(session, domain_settings.domain, computers, ou_guid_map, ou_props,
                                                 domain_settings.nodes, pool.ous)

    ou_props, ou_guid_map = create_users_ous(session, domain_settings.domain, users, ou_guid_map, ou_props,
                                             domain_settings.nodes, pool.ous)

    link_ous_to_domain(session, domain_settings.domain, ou_guid_map)

    print("Creating GPOs")
    gpos = create_gpos(session, domain_settings.domain, gpos)
    link_to_ous(session, gpos, domain_settings.domain, ou_guid_map)
    add_outbound_acls(session, it_groups, it_users, gpos, computers, pool.acls)

    print("Marking some users as Kerberoastable")
    add_kerberoastable_users(session, it_users)

    print("Adding unconstrained delegation to a few computers")
    add_unconstrained_delegation(session, computers)

    session.run("MATCH (n:User) SET n.owned=false")
    session.run("MATCH (n:Computer) SET n.owned=false")
    session.run("MATCH (n) SET n.domain=$domain", domain=domain_settings.domain)

    session.close()

    print("Database Generation Finished!")
