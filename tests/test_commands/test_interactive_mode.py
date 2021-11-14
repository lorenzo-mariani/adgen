#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import sys

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


