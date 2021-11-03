#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import os
import sys


from unittest import mock
from adgen.cl_parser import parse_args
from adgen.default_config import DEFAULT_DB_SETTINGS, DEFAULT_DOMAIN_SETTINGS
from adgen.initializer import initialize
from adgen.utils.loader import check_parameters, get_value_from_ini


def test_parameters():
    # Everything is correct inside correct_config.ini
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'correct_config.ini')
    check = check_parameters(path_to_check)
    assert check == 0

    # Some sections are missing
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'missing_section.ini')
    check = check_parameters(path_to_check)
    assert check == -1

    # Some sections are incorrect
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'wrong_section.ini')
    check = check_parameters(path_to_check)
    assert check == -1

    # Sum of probabilities greater than 100
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'wrong_prob.ini')
    check = check_parameters(path_to_check)
    assert check == -2

    # Probability lower than 0
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'negative_prob.ini')
    check = check_parameters(path_to_check)
    assert check == -2


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
        db_settings, domain_settings, pool = initialize(cmd_params)

    assert db_settings.url == "bolt://localhost:7687"
    assert db_settings.username == "run_user"
    assert db_settings.password == "run_passwd"
    assert domain_settings.nodes == 400
    assert domain_settings.domain == "run_domain.local".upper()

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
        db_settings, domain_settings, pool = initialize(cmd_params)

    assert db_settings.url == get_value_from_ini("CONNECTION", "url", cmd_params.get('conn'))
    assert db_settings.username == get_value_from_ini("CONNECTION", "username", cmd_params.get('conn'))
    assert db_settings.password == get_value_from_ini("CONNECTION", "password", cmd_params.get('conn'))
    assert domain_settings.domain == get_value_from_ini("CONNECTION", "domain", cmd_params.get('conn'))
    assert domain_settings.nodes == get_value_from_ini("CONNECTION", "nodes", cmd_params.get('conn'))

    # Interactive mode
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
