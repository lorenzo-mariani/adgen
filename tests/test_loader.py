#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import os
import sys


from unittest import mock
from adgen.cl_parser import parse_args
from adgen.initializer import initialize
from adgen.config import DEFAULT_CONFIG
from adgen.utils.loader import get_value_from_ini
from adgen.utils.loader import check_parameters


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
