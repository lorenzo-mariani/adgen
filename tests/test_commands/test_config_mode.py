#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import os
import sys
import pytest
import adgen.db as db

from adgen.cl_parser import parse_args
from adgen.commands.config_mode import check_config_args, config
from adgen.initializer import initialize
from adgen.utils.loader import get_value_from_ini
from unittest import mock


def test_config_init():
    """Test if entities are initialized correctly while using config mode"""
    conn_config_path = os.path.join(os.path.abspath('adgen'), 'data', 'conn_config.ini')
    param_config_path = os.path.join(os.path.abspath('adgen'), 'data', 'param_config.ini')

    # Test while using a specific value for the node
    config_args = [
        "adgen",
        "config",
        "--conn", conn_config_path,
        "--param", param_config_path
    ]

    with mock.patch.object(sys, 'argv', config_args):
        args = parse_args(config_args)
        cmd_params = vars(args)
        db_settings, domain_settings, pool = initialize(cmd_params)

    assert db_settings.url == get_value_from_ini("CONNECTION", "url", cmd_params.get('conn'))
    assert db_settings.username == get_value_from_ini("CONNECTION", "username", cmd_params.get('conn'))
    assert db_settings.password == get_value_from_ini("CONNECTION", "password", cmd_params.get('conn'))
    assert domain_settings.domain == get_value_from_ini("CONNECTION", "domain", cmd_params.get('conn'))
    assert domain_settings.nodes == get_value_from_ini("CONNECTION", "nodes", cmd_params.get('conn'))

    # Test while using a distribution for the nodes (in particular, uniform(200,300))
    nodes_distr_path = os.path.join(os.path.abspath('adgen'), 'data', 'config_nodes_distr.yaml')
    config_args = [
        "adgen",
        "config",
        "--conn", conn_config_path,
        "--param", param_config_path,
        "--nodes-distr", nodes_distr_path
    ]

    with mock.patch.object(sys, 'argv', config_args):
        args = parse_args(config_args)
        cmd_params = vars(args)
        db_settings, domain_settings, pool = initialize(cmd_params)

    assert db_settings.url == get_value_from_ini("CONNECTION", "url", cmd_params.get('conn'))
    assert db_settings.username == get_value_from_ini("CONNECTION", "username", cmd_params.get('conn'))
    assert db_settings.password == get_value_from_ini("CONNECTION", "password", cmd_params.get('conn'))
    assert domain_settings.domain == get_value_from_ini("CONNECTION", "domain", cmd_params.get('conn'))
    assert 200 <= domain_settings.nodes <= 300


def test_config_exceptions():
    """Test exceptions while using config mode"""
    conn_config_path = os.path.join(os.path.abspath('adgen'), 'data', 'conn_config.ini')
    param_config_path = os.path.join(os.path.abspath('adgen'), 'data', 'param_config.ini')

    files = ['invalid_path',
             'config_zero_distr_enabled.yaml',
             'config_two_distr_enabled.yaml',
             'config_wrong_distr_keys.yaml',
             'config_wrong_distr.yaml']

    wrong_key = "wrong_key"

    for f in files:
        distr_path = os.path.join(os.path.abspath('tests'), 'data', f)

        config_args = [
            "adgen",
            "config",
            "--conn", conn_config_path,
            "--param", param_config_path,
            "--nodes-distr", distr_path
        ]

        with pytest.raises(Exception) as exc_info:
            with mock.patch.object(sys, 'argv', config_args):
                args = parse_args(config_args)
                cmd_params = vars(args)
                check_config_args(cmd_params)

                if f == 'invalid_path':
                    assert exc_info.value == f"ERROR: Reading From File: file {f} does not exist"
                elif f == 'config_zero_distr_enabled.yaml':
                    assert exc_info.value == f"ERROR: Reading From File: no distribution enabled"
                elif f == 'config_two_distr_enabled.yaml':
                    assert exc_info.value == f"ERROR: Reading From File: more than one distribution enabled"
                elif f == 'config_wrong_distr_keys.yaml':
                    assert exc_info.value == f"Error: Reading From File: wrong {wrong_key} key. Check that only the keys 'distribution', 'x' and 'y' are present"
                elif f == 'config_wrong_distr.yaml':
                    assert exc_info.value == "Error: Reading From File: distribution not available. Available distributions are: uniform, triangular, gauss, gamma"


def test_config_mode():
    """Test the correct behavior of the config mode"""
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

        config(cmd_params)

        domain = {}
        for res in session.run("MATCH (n:Domain) RETURN n.name"):
            domain.update(res)
        assert len(domain) == 1
        assert domain.get('n.name') == get_value_from_ini("CONNECTION", "domain", conn_config_path)

        users = []
        for u in session.run("MATCH (n:User) RETURN n"):
            users.append(u)
        assert len(users) != 0
