#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import sys
import builtins
import pytest

import adgen.db as db

from adgen.cl_parser import parse_args
from adgen.commands.interactive_mode import interactive
from adgen.default_config import DEFAULT_DB_SETTINGS, DEFAULT_DOMAIN_SETTINGS
from adgen.initializer import initialize
from unittest import mock


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


def test_setnodes_distr():
    db_settings, domain_settings, pool = init_entity()

    # If the extremes of the distribution interval are equal,
    # then the generated value must be equal to the extremes
    user_input = ['uniform', '100', '100']
    with mock.patch.object(builtins, 'input', side_effect=user_input):
        db.setnodes_distr(domain_settings)
        assert domain_settings.nodes == 100

    # Entering a value of b lower than the value of a raises an exception
    user_input = ['normal', '200', '100']
    with pytest.raises(Exception) as exc_info:
        with mock.patch.object(builtins, 'input', side_effect=user_input):
            db.setnodes_distr(domain_settings)
            assert exc_info.value == "ERROR: a must be lower than b."

    # Triangular distribution
    user_input = ['triangular', '500', '1000']
    with mock.patch.object(builtins, 'input', side_effect=user_input):
        db.setnodes_distr(domain_settings)
        assert 500 <= domain_settings.nodes <= 1000

    # A too small value is generated, so the number of nodes must be equal
    # to the last set value (in this case between 500 and 1000 due to the
    # triangular distribution above)
    user_input = ['gauss', '50', '5']
    with mock.patch.object(builtins, 'input', side_effect=user_input):
        db.setnodes_distr(domain_settings)
        assert 500 <= domain_settings.nodes <= 1000

    # Entering a negative value of mu raises an exception
    user_input = ['normal', '-100', '20']
    with pytest.raises(Exception) as exc_info:
        with mock.patch.object(builtins, 'input', side_effect=user_input):
            db.setnodes_distr(domain_settings)
            assert exc_info.value == "ERROR: mu and sigma must be positive."


def test_setdomain():
    db_settings, domain_settings, pool = init_entity()

    with mock.patch.object(builtins, 'input', lambda _: 'CONTOSO.LOCAL'):
        db.setdomain(domain_settings)
        assert domain_settings.domain == 'contoso.local'.upper()


def test_dbconfig():
    db_settings, domain_settings, pool = init_entity()

    user_input = ['different_url', 'different_username', 'different_password']

    with mock.patch.object(builtins, 'input', side_effect=user_input):
        db.dbconfig(db_settings)
        assert db_settings.url == 'different_url'
        assert db_settings.username == 'different_username'
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


def test_interactive_init():
    interactive_args = [
        "adgen",
        "interactive"
    ]

    with mock.patch.object(sys, 'argv', interactive_args):
        args = parse_args(interactive_args)
        cmd_params = vars(args)
        db_settings, domain_settings, pool = initialize(cmd_params)

    assert db_settings.url == DEFAULT_DB_SETTINGS.get('url')
    assert db_settings.username == DEFAULT_DB_SETTINGS.get('username')
    assert db_settings.password == DEFAULT_DB_SETTINGS.get('password')
    assert domain_settings.nodes == DEFAULT_DOMAIN_SETTINGS.get('nodes')
    assert domain_settings.domain == DEFAULT_DOMAIN_SETTINGS.get('domain')


