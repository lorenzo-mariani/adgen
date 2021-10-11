import os
import pickle
import random
import time

import adgen.db as db
from neo4j import GraphDatabase
from adgen.utils.utils import get_list_from_ini, cs, cn
from adgen.entities.entity import Entity


def get_names(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def init_entity():
    data_path = os.path.abspath("..\\adgen\\data")
    entity = Entity()
    entity.url = 'bolt://localhost:7687'
    entity.username = 'neo4j'
    entity.password = 'neo4jpwd'
    entity.driver = None
    entity.connected = False
    entity.nodes = 500
    entity.domain = 'TESTLAB.LOCAL'
    entity.sid = 'S-1-5-21-883232822-274137685-4173207997'
    entity.current_time = int(time.time())
    entity.first_names = get_names(data_path + "\\first.pkl")
    entity.last_names = get_names(data_path + "\\last.pkl")
    entity.clients_os = get_list_from_ini("CLIENTS", data_path + "\\default_config.ini")
    entity.servers_os = get_list_from_ini("SERVERS", data_path + "\\default_config.ini")
    entity.acls = get_list_from_ini("ACLS", data_path + "\\default_config.ini")
    entity.groups = get_list_from_ini("GROUPS", data_path + "\\default_config.ini")
    entity.ous = get_list_from_ini("OUS", data_path + "\\default_config.ini")

    return entity


def test_connection():
    entity = init_entity()

    if entity.driver is not None:
        entity.driver.close()

    if GraphDatabase.driver(entity.url, auth=(entity.username, entity.password)):
        entity.connected = True

    assert entity.connected is True


def test_cleardb():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()

    session.run("match (a) -[r] -> () delete a, r")  # delete all nodes with relationships
    session.run("match (a) delete a")  # delete nodes that have no relationships

    result = []
    for r in session.run("MATCH (n) RETURN n"):
        result.append(r)
    assert len(result) == 0


def test_users():
    entity = init_entity()
    users = []
    props = []
    ridcount = 0

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    result = []
    for r in session.run("MATCH (n:User) RETURN n"):
        result.append(r)
    assert len(result) == 0

    for i in range(1, entity.nodes + 1):
        first = random.choice(entity.first_names)
        last = random.choice(entity.last_names)
        user_name = "{}{}{:05d}@{}".format(first[0], last, i, entity.domain).upper()
        user_name = user_name.format(first[0], last, i).upper()
        users.append(user_name)
        dispname = "{} {}".format(first, last)
        ridcount += 1
        objectsid = cs(ridcount, entity.sid)
        user_properties = {
            'id': objectsid,
            'props': {
                'displayname': dispname
            }
        }
        props.append(user_properties)

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid:prop.id})
                SET n:User, n += prop.props
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Base {objectid:prop.id})
        SET n:User, n += prop.props
        """,
        props=props
    )

    assert len(users) == entity.nodes

    result = []
    for r in session.run("MATCH (n:User) RETURN n"):
        result.append(r)
    assert len(result) == len(users)

    das = db.add_domain_admins(session, entity.domain, entity.nodes, users)

    groups = []
    props = []
    ridcount = 0

    for i in range(1, entity.nodes + 1):
        group = random.choice(entity.groups)
        group_name = "{}{:05d}@{}".format(group, i, entity.domain)
        groups.append(group_name)
        sid = cs(ridcount, entity.sid)
        ridcount += 1
        group_props = {
            "name": group_name,
            "id": sid
        }
        props.append(group_props)

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid:prop.id})
                SET n:Group, n.name=prop.name
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Base {objectid:prop.id})
        SET n:Group, n.name=prop.name
        """,
        props=props
    )

    it_users = db.add_users_to_group(session, entity.nodes, users, groups, das, entity.groups)

    result = []
    for r in session.run("MATCH (n) WHERE (n.hasspn) RETURN n"):
        result.append(r)
    assert len(result) == 0

    i = random.randint(10, 20)
    i = min(i, len(it_users))
    for user in random.sample(it_users, i):
        session.run(
            """
            MATCH (n:User {name:$user})
            SET n.hasspn=true
            """,
            user=user
        )

    result = []
    for r in session.run("MATCH (n) WHERE (n.hasspn) RETURN n"):
        result.append(r)
    assert len(result) != 0


def test_computers():
    entity = init_entity()
    computers = []
    props = []
    ridcount = 0

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    result = []
    for r in session.run("MATCH (n:Computer) RETURN n"):
        result.append(r)
    assert len(result) == 0

    for i in range(1, entity.nodes + 1):
        comp_name = "COMP{:05d}.{}".format(i, entity.domain)
        computers.append(comp_name)
        os = random.choice(entity.clients_os)
        computer_props = {
            "id": cs(ridcount, entity.sid),
            "props": {
                "name": comp_name,
                "operatingsystem": os
            }
        }
        props.append(computer_props)
        ridcount += 1

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid: prop.id})
                SET n:Computer, n += prop.props
                """,
                props=props
            )
            props = []
    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Base {objectid:prop.id})
        SET n:Computer, n += prop.props
        """,
        props=props
    )

    assert len(computers) == entity.nodes

    result = []
    for r in session.run("MATCH (n:Computer) RETURN n"):
        result.append(r)
    assert len(result) == len(computers)

    dcs = []

    for ou in entity.ous:
        comp_name = cn(f"{ou}LABDC", entity.domain)
        sid = cs(ridcount, entity.sid)
        os = random.choice(entity.servers_os)

        dc_props = {
            "name": comp_name,
            "id": sid,
            "operatingsystem": os,
        }
        ridcount += 1
        dcs.append(dc_props)

        session.run(
            """
            MERGE (n:Base {objectid:$sid})
            SET n:Computer,n.name=$name, n.operatingsystem=$os
            """,
            sid=sid,
            name=comp_name,
            os=dc_props["operatingsystem"]
        )

    assert dcs is not None


def test_groups():
    entity = init_entity()
    groups = []
    props = []
    ridcount = 0

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    result = []
    for r in session.run("MATCH (n:Group) RETURN n"):
        result.append(r)
    assert len(result) == 0

    for i in range(1, entity.nodes + 1):
        group = random.choice(entity.groups)
        group_name = "{}{:05d}@{}".format(group, i, entity.domain)
        groups.append(group_name)
        sid = cs(ridcount, entity.sid)
        ridcount += 1
        group_props = {
            "name": group_name,
            "id": sid
        }
        props.append(group_props)

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid:prop.id})
                SET n:Group, n.name=prop.name
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Base {objectid:prop.id})
        SET n:Group, n.name=prop.name
        """,
        props=props
    )

    assert len(groups) == entity.nodes

    result = []
    for r in session.run("MATCH (n:Group) RETURN n"):
        result.append(r)
    assert len(result) == len(groups)


def test_gpos():
    entity = init_entity()
    gpos = []

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    result = []
    for r in session.run("MATCH (n:GPO) RETURN n"):
        result.append(r)
    assert len(result) == 0

    for i in range(1, 20):
        gpo_name = "GPO_{}@{}".format(i, entity.domain)
        session.run(
            """
            MERGE (n:Base {name:$gponame})
            SET n:GPO
            """,
            gponame=gpo_name
        )
        gpos.append(gpo_name)

    assert len(gpos) != 0

    result = []

    for r in session.run("MATCH (n:GPO) RETURN n"):
        result.append(r)

    assert len(result) == len(gpos)
