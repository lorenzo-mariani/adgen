#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import os
import sys
import uuid
import builtins
import adgen.db as db

from unittest import mock
from adgen.cl_parser import parse_args
from adgen.initializer import initialize
from adgen.config import DEFAULT_CONFIG
from adgen.utils.utils import get_value_from_ini


def test_commands():
    # Run mode
    run_args = [
        "adgen",
        "run",
        "--url", "bolt://localhost:7687",
        "--user", "run_user",
        "--passwd", "run_passwd",
        "--nodes", "400",
        "--domain", "run_domain.local"
    ]

    with mock.patch.object(sys, 'argv', run_args):
        args = parse_args(run_args)
        cmd_params = vars(args)
        entity = initialize(cmd_params)

    assert entity.url == "bolt://localhost:7687"
    assert entity.username == "run_user"
    assert entity.password == "run_passwd"
    assert entity.nodes == 400
    assert entity.domain == "run_domain.local".upper()

    # Config mode
    conn_config_path = os.path.join(os.path.abspath('adgen'), 'data', 'conn_config.ini')
    param_config_path = os.path.join(os.path.abspath('adgen'), 'data', 'param_config.ini')
    config_args = [
        "adgen",
        "config",
        "--conn", conn_config_path,
        "--param", param_config_path
    ]

    with mock.patch.object(sys, 'argv', config_args):
        args = parse_args(config_args)
        cmd_params = vars(args)
        entity = initialize(cmd_params)

    assert entity.url == get_value_from_ini("CONNECTION", "url", cmd_params.get('conn'))
    assert entity.username == get_value_from_ini("CONNECTION", "username", cmd_params.get('conn'))
    assert entity.password == get_value_from_ini("CONNECTION", "password", cmd_params.get('conn'))
    assert entity.domain == get_value_from_ini("CONNECTION", "domain", cmd_params.get('conn'))
    assert entity.nodes == get_value_from_ini("CONNECTION", "nodes", cmd_params.get('conn'))

    # Interactive mode
    interactive_args = [
        "adgen",
        "interactive"
    ]

    with mock.patch.object(sys, 'argv', interactive_args):
        args = parse_args(interactive_args)
        cmd_params = vars(args)
        entity = initialize(cmd_params)

    assert entity.url == DEFAULT_CONFIG.get('url')
    assert entity.username == DEFAULT_CONFIG.get('username')
    assert entity.password == DEFAULT_CONFIG.get('password')
    assert entity.nodes == DEFAULT_CONFIG.get('nodes')
    assert entity.domain == DEFAULT_CONFIG.get('domain')


def init_entity():
    interactive_args = [
        "adgen",
        "interactive"
    ]

    with mock.patch.object(sys, 'argv', interactive_args):
        args = parse_args(interactive_args)
        cmd_params = vars(args)
        entity = initialize(cmd_params)

    return entity


def test_setnodes():
    entity = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: '300'):
        db.setnodes(entity)
        assert entity.nodes == 300


def test_setdomain():
    entity = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: 'CONTOSO.LOCAL'):
        db.setdomain(entity)
        assert entity.domain == 'contoso.local'.upper()


def test_dbconfig():
    entity = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: 'different_url'):
        db.dbconfig(entity)
        assert entity.url == 'different_url'

    with mock.patch.object(builtins, 'input', lambda _: 'different_username'):
        db.dbconfig(entity)
        assert entity.username == 'different_username'

    with mock.patch.object(builtins, 'input', lambda _: 'different_password'):
        db.dbconfig(entity)
        assert entity.password == 'different_password'


def test_connection():
    entity = init_entity()

    db.test_db_connection(entity)
    assert entity.connected is True


def test_cleardb():
    entity = init_entity()

    db.connect(entity)
    session = entity.driver.session()

    session.run("match (a) -[r] -> () delete a, r")  # delete all nodes with relationships
    session.run("match (a) delete a")  # delete nodes that have no relationships

    result = []
    for r in session.run("MATCH (n) RETURN n"):
        result.append(r)
    assert len(result) == 0


def test_computers():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    computers = []
    users = []
    groups = []
    dcou = str(uuid.uuid4())

    # Create computers
    computers_props, computers, ridcount = db.create_computers(session, entity.domain, entity.sid, entity.nodes, computers, entity.clients_os)
    assert len(computers) == entity.nodes

    # Create domain controllers
    dcs_props, ridcount = db.create_dcs(session, entity.domain, entity.sid, dcou, ridcount, entity.servers_os, entity.ous)
    assert len(dcs_props) != 0

    # Add RDP / DCOM / Delegate To
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    groups_props, groups, ridcount = db.create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount, entity.groups)
    das = db.add_domain_admins(session, entity.domain, entity.nodes, users)
    it_users = db.add_users_to_group(session, entity.nodes, users, groups, das, entity.groups)
    it_groups = db.add_local_admin_rights(session, groups, computers)
    db.add_rdp_dcom_delegate(session, computers, it_users, it_groups)

    result_can_rdp = []
    result_execute_dcom = []
    result_allowed_to_delegate = []
    result_has_session = []

    for r in session.run("MATCH p=()-[r:CanRDP]->() RETURN p"):
        result_can_rdp.append(r)

    for r in session.run("MATCH p=()-[r:ExecuteDCOM]->() RETURN p"):
        result_execute_dcom.append(r)

    for r in session.run("MATCH p=()-[r:AllowedToDelegate]->() RETURN p"):
        result_allowed_to_delegate.append(r)

    for r in session.run("MATCH p = () - [r:HasSession]->() RETURN p"):
        result_has_session.append(r)

    assert len(result_can_rdp) != 0
    assert len(result_execute_dcom) != 0
    assert len(result_allowed_to_delegate) != 0
    assert len(result_has_session) == 0

    # Add sessions
    db.add_sessions(session, entity.nodes, computers, users, das)
    result = []
    for r in session.run("MATCH p = () - [r:HasSession]->() RETURN p"):
        result.append(r)
    assert len(result) != 0

    # Add uncontrained delegation
    db.add_unconstrained_delegation(session, computers)
    result = []
    for r in session.run("MATCH (n) WHERE (n.unconstrainteddelegation) RETURN n"):
        result.append(r)
    assert len(result) != 0


def test_users():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    users = []
    groups = []
    ridcount = 0

    # Create users
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    result = []
    for r in session.run("MATCH (n:User) RETURN n"):
        result.append(r)
    assert len(users) == entity.nodes
    assert len(result) == len(users)

    # Add kerberoastable users
    groups_props, groups, ridcount = db.create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount, entity.groups)
    das = db.add_domain_admins(session, entity.domain, entity.nodes, users)
    it_users = db.add_users_to_group(session, entity.nodes, users, groups, das, entity.groups)
    db.add_kerberoastable_users(session, it_users)
    result = []
    for r in session.run("MATCH (n) WHERE (n.hasspn) RETURN n"):
        result.append(r)
    assert len(result) != 0


def test_groups():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    groups = []
    users = []
    ridcount = 0

    # Data generation
    db.data_generation(session, entity.domain, entity.sid)
    result = []
    for r in session.run("MATCH (n) RETURN n"):
        result.append(r)
    assert len(result) != 0

    # Create groups
    groups_props, groups, ridcount = db.create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount, entity.groups)
    assert len(groups) == entity.nodes

    # Create nested groups
    db.create_nested_groups(session, entity.nodes, groups)
    result = []
    for r in session.run("MATCH p=()-[r:MemberOf]->() RETURN p"):
        result.append(r)
    assert len(result) != 0

    # Add domain admins
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    das = db.add_domain_admins(session, entity.domain, entity.nodes, users)
    assert len(das) != 0

    # Add users to group
    it_users = db.add_users_to_group(session, entity.nodes, users, groups, das, entity.groups)
    assert len(it_users) != 0


def test_ous():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    ou_guid_map = {}
    ou_props = []
    users = []
    computers = []
    ridcount = 0
    dcou = str(uuid.uuid4())

    # Create dcs OUs
    db.create_dcs_ous(session, entity.domain, dcou)
    result = []
    for r in session.run("MATCH (n:OU) RETURN n"):
        result.append(r)
    assert len(result) != 0

    # Create computers OUs and create users OUs
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    computers_props, computers, ridcount = db.create_computers(session, entity.domain, entity.sid, entity.nodes, computers, entity.clients_os)
    ou_props, ou_guid_map = db.create_computers_ous(session, entity.domain, computers, ou_guid_map, ou_props, entity.nodes, entity.ous)
    ou_props, ou_guid_map = db.create_users_ous(session, entity.domain, users, ou_guid_map, ou_props, entity.nodes, entity.ous)
    assert len(ou_props) == 2 * entity.nodes

    # Link OUs to domain
    db.link_ous_to_domain(session, entity.domain, ou_guid_map)
    result = []
    for r in session.run("MATCH (n:Domain) WITH n MATCH (m:OU) WITH m MATCH p=()-[r:Contains]->() RETURN m"):
        result.append(r)
    assert len(result) != 0


def test_gpos():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    gpos = []
    ou_guid_map = {}
    ou_props = []
    users = []
    computers = []
    ridcount = 0
    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())

    # Create default GPOs
    db.create_default_gpos(session, entity.domain, ddp, ddcp)
    result = []
    for r in session.run("MATCH (n:GPO) RETURN n"):
        result.append(r)
    assert len(result) != 0

    default_gpos = len(result)

    # Create GPOs
    gpos = db.create_gpos(session, entity.domain, gpos)
    assert len(gpos) != 0

    result = []
    for r in session.run("MATCH (n:GPO) RETURN n"):
        result.append(r)
    assert len(result) == len(gpos) + default_gpos

    # Link GPOs to OUs
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    computers_props, computers, ridcount = db.create_computers(session, entity.domain, entity.sid, entity.nodes, computers, entity.clients_os)
    ou_props, ou_guid_map = db.create_computers_ous(session, entity.domain, computers, ou_guid_map, ou_props, entity.nodes, entity.ous)
    ou_props, ou_guid_map = db.create_users_ous(session, entity.domain, users, ou_guid_map, ou_props, entity.nodes, entity.ous)
    db.link_to_ous(session, gpos, entity.domain, ou_guid_map)
    result = []
    for r in session.run("MATCH (n:OU) WITH n MATCH (m:GPO) WITH n,m MATCH (m)-[:GpLink]->(n) return m"):
        result.append(r)
    assert len(result) != 0


def test_acls():
    entity = init_entity()

    db.test_db_connection(entity)
    session = entity.driver.session()
    db.cleardb(entity, "a")

    groups = []
    computers = []
    users = []
    gpos = []
    ridcount = 0
    dcou = str(uuid.uuid4())
    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())

    # Add standard edges
    db.add_standard_edges(session, entity.domain, dcou)

    result_generic_all = []
    result_owns = []
    result_write_owner = []
    result_write_dacl = []
    result_dcsync = []
    result_get_changes = []
    result_get_changes_all = []

    for r in session.run("MATCH p=()-[r:GenericAll]->() RETURN p"):
        result_generic_all.append(r)

    for r in session.run("MATCH p=()-[r:Owns]->() RETURN p"):
        result_owns.append(r)

    for r in session.run("MATCH p=()-[r:WriteOwner]->() RETURN p"):
        result_write_owner.append(r)

    for r in session.run("MATCH p=()-[r:WriteDacl]->() RETURN p"):
        result_write_dacl.append(r)

    for r in session.run("MATCH p=()-[r:DCSync]->() RETURN p"):
        result_dcsync.append(r)

    for r in session.run("MATCH p=()-[r:GetChanges]->() RETURN p"):
        result_get_changes.append(r)

    for r in session.run("MATCH p=()-[r:GetChangesAll]->() RETURN p"):
        result_get_changes_all.append(r)

    assert len(result_generic_all) != 0
    assert len(result_owns) != 0
    assert len(result_write_owner) != 0
    assert len(result_write_dacl) != 0
    assert len(result_dcsync) != 0
    assert len(result_get_changes) != 0
    assert len(result_get_changes_all) != 0

    # Add domain admin
    groups_props, groups, ridcount = db.create_groups(session, entity.domain, entity.sid, entity.nodes, groups, ridcount, entity.groups)
    computers_props, computers, ridcount = db.create_computers(session, entity.domain, entity.sid, entity.nodes,computers, entity.clients_os)
    db.add_domain_admin_to_local_admin(session, entity.sid)
    result = []
    for r in session.run("MATCH p=()-[r:AdminTo]->() RETURN p"):
        result.append(r)
    assert len(result) != 0

    # Add local admin rights
    it_groups = db.add_local_admin_rights(session, groups, computers)
    assert len(it_groups) != 0

    # Add domain admin ACEs
    user_props, users, ridcount = db.create_users(session, entity.domain, entity.sid, entity.nodes, entity.current_time, entity.first_names, entity.last_names, users, ridcount)
    db.add_domain_admin_aces(session, entity.domain, computers, users, groups)

    # Add outbound ACLs
    db.create_default_gpos(session, entity.domain, ddp, ddcp)
    gpos = db.create_gpos(session, entity.domain, gpos)
    das = db.add_domain_admins(session, entity.domain, entity.nodes, users)
    it_users = db.add_users_to_group(session, entity.nodes, users, groups, das, entity.groups)
    db.add_outbound_acls(session, it_groups, it_users, gpos, computers, entity.acls)
