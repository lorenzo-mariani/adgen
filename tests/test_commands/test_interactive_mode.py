#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import builtins
import sys

import pytest

import adgen.db as db

from adgen.cl_parser import parse_args
from adgen.commands.interactive_mode import interactive
from adgen.default_config import DEFAULT_DB_SETTINGS, DEFAULT_DOMAIN_SETTINGS
from adgen.initializer import initialize
from unittest import mock


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


def test_interactive_mode():
    interactive_args = [
        "adgen",
        "interactive"
    ]

    with mock.patch.object(sys, 'argv', interactive_args):
        args = parse_args(interactive_args)
        cmd_params = vars(args)
        db_settings, domain_settings, pool = initialize(cmd_params)

        db.test_db_connection(db_settings)
        session = db_settings.driver.session()
        db.cleardb(db_settings, "a")

        domain = {}
        for res in session.run("MATCH (n:Domain) RETURN n.name"):
            domain.update(res)
        assert len(domain) == 0

        users = []
        for u in session.run("MATCH (n:User) RETURN n"):
            users.append(u)
        assert len(users) == 0

        commands = [
            "connect",
            "clear_and_generate",
            "exit"
        ]

        with mock.patch.object(builtins, 'input', side_effect=commands):
            try:
                interactive(cmd_params)
            except KeyboardInterrupt:
                pass

        domain = {}
        for res in session.run("MATCH (n:Domain) RETURN n.name"):
            domain.update(res)

        assert len(domain) == 1
        assert domain.get('n.name') == 'TESTLAB.LOCAL'

        users = []
        for u in session.run("MATCH (n:User) RETURN n"):
            users.append(u)
        assert len(users) != 0

