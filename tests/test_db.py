#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import sys
import uuid
import builtins
import adgen.db as db

from unittest import mock
from adgen.cl_parser import parse_args
from adgen.initializer import initialize


def init_entity():
    interactive_args = [
        "adgen",
        "interactive"
    ]

    with mock.patch.object(sys, 'argv', interactive_args):
        args = parse_args(interactive_args)
        cmd_params = vars(args)
        db_settings, domain_settings, pool = initialize(cmd_params)

    return db_settings, domain_settings, pool


def test_setnodes():
    db_settings, domain_settings, pool = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: '300'):
        db.setnodes(domain_settings)
        assert domain_settings.nodes == 300


def test_setdomain():
    db_settings, domain_settings, pool = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: 'CONTOSO.LOCAL'):
        db.setdomain(domain_settings)
        assert domain_settings.domain == 'contoso.local'.upper()


def test_dbconfig():
    db_settings, domain_settings, pool = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: 'different_url'):
        db.dbconfig(db_settings)
        assert db_settings.url == 'different_url'

    with mock.patch.object(builtins, 'input', lambda _: 'different_username'):
        db.dbconfig(db_settings)
        assert db_settings.username == 'different_username'

    with mock.patch.object(builtins, 'input', lambda _: 'different_password'):
        db.dbconfig(db_settings)
        assert db_settings.password == 'different_password'


def test_connection():
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    assert db_settings.connected is True


def test_cleardb():
    db_settings, domain_settings, pool = init_entity()
    db.connect(db_settings)
    session = db_settings.driver.session()

    session.run("match (a) -[r] -> () delete a, r")  # delete all nodes with relationships
    session.run("match (a) delete a")  # delete nodes that have no relationships

    result = []
    for r in session.run("MATCH (n) RETURN n"):
        result.append(r)
    assert len(result) == 0


def test_computers():
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    session = db_settings.driver.session()
    db.cleardb(db_settings, "a")

    computers = []
    users = []
    groups = []
    dcou = str(uuid.uuid4())

    # Create computers
    computers_props, computers, ridcount = db.create_computers(session, domain_settings.domain, domain_settings.sid,
                                                               domain_settings.nodes, computers, pool.clients_os)
    assert len(computers) == domain_settings.nodes

    # Create domain controllers
    dcs_props, ridcount = db.create_dcs(session, domain_settings.domain, domain_settings.sid, dcou, ridcount,
                                        pool.servers_os, pool.ous)
    assert len(dcs_props) != 0

    # Add RDP / DCOM / Delegate To
    user_props, users, ridcount = db.create_users(session, domain_settings.domain, domain_settings.sid,
                                                  domain_settings.nodes, domain_settings.current_time, pool.first_names,
                                                  pool.last_names, users, ridcount)

    groups_props, groups, ridcount = db.create_groups(session, domain_settings.domain, domain_settings.sid,
                                                      domain_settings.nodes, groups, ridcount, pool.groups)

    das = db.add_domain_admins(session, domain_settings.domain, domain_settings.nodes, users)
    it_users = db.add_users_to_group(session, domain_settings.nodes, users, groups, das, pool.groups)
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
    db.add_sessions(session, domain_settings.nodes, computers, users, das)

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
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    session = db_settings.driver.session()
    db.cleardb(db_settings, "a")

    users = []
    groups = []
    ridcount = 0

    # Create users
    user_props, users, ridcount = db.create_users(session, domain_settings.domain, domain_settings.sid,
                                                  domain_settings.nodes, domain_settings.current_time, pool.first_names,
                                                  pool.last_names, users, ridcount)

    result = []
    for r in session.run("MATCH (n:User) RETURN n"):
        result.append(r)
    assert len(users) == domain_settings.nodes
    assert len(result) == len(users)

    # Add kerberoastable users
    groups_props, groups, ridcount = db.create_groups(session, domain_settings.domain, domain_settings.sid,
                                                      domain_settings.nodes, groups, ridcount, pool.groups)
    das = db.add_domain_admins(session, domain_settings.domain, domain_settings.nodes, users)
    it_users = db.add_users_to_group(session, domain_settings.nodes, users, groups, das, pool.groups)
    db.add_kerberoastable_users(session, it_users)

    result = []
    for r in session.run("MATCH (n) WHERE (n.hasspn) RETURN n"):
        result.append(r)
    assert len(result) != 0


def test_groups():
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    session = db_settings.driver.session()
    db.cleardb(db_settings, "a")

    groups = []
    users = []
    ridcount = 0

    # Data generation
    db.data_generation(session, domain_settings.domain, domain_settings.sid)

    result = []
    for r in session.run("MATCH (n) RETURN n"):
        result.append(r)
    assert len(result) != 0

    # Create groups
    groups_props, groups, ridcount = db.create_groups(session, domain_settings.domain, domain_settings.sid,
                                                      domain_settings.nodes, groups, ridcount, pool.groups)
    assert len(groups) == domain_settings.nodes

    # Create nested groups
    db.create_nested_groups(session, domain_settings.nodes, groups)

    result = []
    for r in session.run("MATCH p=()-[r:MemberOf]->() RETURN p"):
        result.append(r)
    assert len(result) != 0

    # Add domain admins
    user_props, users, ridcount = db.create_users(session, domain_settings.domain, domain_settings.sid,
                                                  domain_settings.nodes, domain_settings.current_time,
                                                  pool.first_names, pool.last_names, users, ridcount)

    das = db.add_domain_admins(session, domain_settings.domain, domain_settings.nodes, users)
    assert len(das) != 0

    # Add users to group
    it_users = db.add_users_to_group(session, domain_settings.nodes, users, groups, das, pool.groups)
    assert len(it_users) != 0


def test_ous():
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    session = db_settings.driver.session()
    db.cleardb(db_settings, "a")

    ou_guid_map = {}
    ou_props = []
    users = []
    computers = []
    ridcount = 0
    dcou = str(uuid.uuid4())

    # Create dcs OUs
    db.create_dcs_ous(session, domain_settings.domain, dcou)

    result = []
    for r in session.run("MATCH (n:OU) RETURN n"):
        result.append(r)
    assert len(result) != 0

    # Create computers OUs and create users OUs
    user_props, users, ridcount = db.create_users(session, domain_settings.domain, domain_settings.sid,
                                                  domain_settings.nodes, domain_settings.current_time,
                                                  pool.first_names, pool.last_names, users, ridcount)

    computers_props, computers, ridcount = db.create_computers(session, domain_settings.domain, domain_settings.sid,
                                                               domain_settings.nodes, computers, pool.clients_os)

    ou_props, ou_guid_map = db.create_computers_ous(session, domain_settings.domain, computers, ou_guid_map, ou_props,
                                                    domain_settings.nodes, pool.ous)

    ou_props, ou_guid_map = db.create_users_ous(session, domain_settings.domain, users, ou_guid_map, ou_props,
                                                domain_settings.nodes, pool.ous)

    assert len(ou_props) == 2 * domain_settings.nodes

    # Link OUs to domain
    db.link_ous_to_domain(session, domain_settings.domain, ou_guid_map)

    result = []
    for r in session.run("MATCH (n:Domain) WITH n MATCH (m:OU) WITH m MATCH p=()-[r:Contains]->() RETURN m"):
        result.append(r)
    assert len(result) != 0


def test_gpos():
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    session = db_settings.driver.session()
    db.cleardb(db_settings, "a")

    gpos = []
    ou_guid_map = {}
    ou_props = []
    users = []
    computers = []
    ridcount = 0
    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())

    # Create default GPOs
    db.create_default_gpos(session, domain_settings.domain, ddp, ddcp)

    result = []
    for r in session.run("MATCH (n:GPO) RETURN n"):
        result.append(r)
    assert len(result) != 0

    default_gpos = len(result)

    # Create GPOs
    gpos = db.create_gpos(session, domain_settings.domain, gpos)
    assert len(gpos) != 0

    result = []
    for r in session.run("MATCH (n:GPO) RETURN n"):
        result.append(r)
    assert len(result) == len(gpos) + default_gpos

    # Link GPOs to OUs
    user_props, users, ridcount = db.create_users(session, domain_settings.domain, domain_settings.sid,
                                                  domain_settings.nodes, domain_settings.current_time,
                                                  pool.first_names, pool.last_names, users, ridcount)

    computers_props, computers, ridcount = db.create_computers(session, domain_settings.domain, domain_settings.sid,
                                                               domain_settings.nodes, computers, pool.clients_os)

    ou_props, ou_guid_map = db.create_computers_ous(session, domain_settings.domain, computers, ou_guid_map, ou_props,
                                                    domain_settings.nodes, pool.ous)

    ou_props, ou_guid_map = db.create_users_ous(session, domain_settings.domain, users, ou_guid_map, ou_props,
                                                domain_settings.nodes, pool.ous)

    db.link_to_ous(session, gpos, domain_settings.domain, ou_guid_map)

    result = []
    for r in session.run("MATCH (n:OU) WITH n MATCH (m:GPO) WITH n,m MATCH (m)-[:GpLink]->(n) return m"):
        result.append(r)
    assert len(result) != 0


def test_acls():
    db_settings, domain_settings, pool = init_entity()

    db.test_db_connection(db_settings)
    session = db_settings.driver.session()
    db.cleardb(db_settings, "a")

    groups = []
    computers = []
    users = []
    gpos = []
    ridcount = 0
    dcou = str(uuid.uuid4())
    ddp = str(uuid.uuid4())
    ddcp = str(uuid.uuid4())

    # Add standard edges
    db.add_standard_edges(session, domain_settings.domain, dcou)

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
    groups_props, groups, ridcount = db.create_groups(session, domain_settings.domain, domain_settings.sid,
                                                      domain_settings.nodes, groups, ridcount, pool.groups)

    computers_props, computers, ridcount = db.create_computers(session, domain_settings.domain, domain_settings.sid,
                                                               domain_settings.nodes, computers, pool.clients_os)

    db.add_domain_admin_to_local_admin(session, domain_settings.sid)

    result = []
    for r in session.run("MATCH p=()-[r:AdminTo]->() RETURN p"):
        result.append(r)
    assert len(result) != 0

    # Add local admin rights
    it_groups = db.add_local_admin_rights(session, groups, computers)
    assert len(it_groups) != 0

    # Add domain admin ACEs
    user_props, users, ridcount = db.create_users(session, domain_settings.domain, domain_settings.sid,
                                                  domain_settings.nodes, domain_settings.current_time,
                                                  pool.first_names, pool.last_names, users, ridcount)

    db.add_domain_admin_aces(session, domain_settings.domain, computers, users, groups)

    # Add outbound ACLs
    db.create_default_gpos(session, domain_settings.domain, ddp, ddcp)
    gpos = db.create_gpos(session, domain_settings.domain, gpos)
    das = db.add_domain_admins(session, domain_settings.domain, domain_settings.nodes, users)
    it_users = db.add_users_to_group(session, domain_settings.nodes, users, groups, das, pool.groups)
    db.add_outbound_acls(session, it_groups, it_users, gpos, computers, pool.acls)
