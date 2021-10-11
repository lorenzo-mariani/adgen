import os
import pickle
import time
import uuid

import adgen.db as db
from neo4j import GraphDatabase
from adgen.utils.utils import get_list_from_ini
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


def test_create_computers():
    entity = init_entity()
    computers = []

    db.test_db_connection(entity)
    session = entity.driver.session()
    computers_props, computers, ridcount = db.create_computers(session, entity.domain, entity.sid, entity.nodes, computers, entity.clients_os)

    assert len(computers) == entity.nodes


def test_create_dcs():
    entity = init_entity()
    ridcount = 0
    dcou = str(uuid.uuid4())

    db.test_db_connection(entity)
    session = entity.driver.session()
    dcs_props, ridcount = db.create_dcs(session, entity.domain, entity.sid, dcou, ridcount, entity.servers_os, entity.ous)

    assert dcs_props is not None


def test_create_users():
    entity = init_entity()
    users = []
    ridcount = 0

    db.test_db_connection(entity)
    session = entity.driver.session()
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)

    assert len(users) == entity.nodes


def test_create_groups():
    entity = init_entity()
    groups = []
    ridcount = 0

    db.test_db_connection(entity)
    session = entity.driver.session()
    groups_props, groups, ridcount = db.create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount, entity.groups)

    assert len(groups) == entity.nodes


def test_create_gpos():
    entity = init_entity()
    gpos = []

    db.test_db_connection(entity)
    session = entity.driver.session()
    gpos = db.create_gpos(session, entity.domain, gpos)

    assert len(gpos) != 0


def test_create_ous():
    entity = init_entity()
    users = []
    computers = []
    ou_guid_map = {}
    ou_props = []

    db.test_db_connection(entity)
    session = entity.driver.session()
    computers_props, computers, ridcount = db.create_computers(session, entity.domain, entity.sid, entity.nodes, computers, entity.clients_os)
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    ou_props, ou_guid_map = db.create_computers_ous(session, entity.domain, computers, ou_guid_map, ou_props, entity.nodes, entity.ous)
    ou_props, ou_guid_map = db.create_users_ous(session, entity.domain, users, ou_guid_map, ou_props, entity.nodes, entity.ous)

    assert len(ou_props) == 2 * entity.nodes
