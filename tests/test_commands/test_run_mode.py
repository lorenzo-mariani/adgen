#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# adgen test suite
# Copyright © 2021, Lorenzo Mariani.
# See /LICENSE for licensing information.

import adgen.db as db
import pytest
import sys

from adgen.cl_parser import parse_args
from adgen.commands.run_mode import check_run_args, run
from adgen.initializer import initialize
from unittest import mock


def test_run_init():
    """Test if entities are initialized correctly while using run mode"""
    run_args = [
        "adgen",
        "run",
        "--url", "bolt://localhost:7687",
        "--user", "run_user",
        "--passwd", "run_passwd",
        "--nodes-val", "400",
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


def test_run_exceptions():
    """Test exceptions while using run mode"""
    # Check if an exception is thrown when neither --nodes-val nor --nodes-distr is inserted
    run_args = [
        "adgen",
        "run",
        "--url", "bolt://localhost:7687",
        "--user", "run_user",
        "--passwd", "run_passwd",
        "--domain", "run_domain.local"
    ]

    with pytest.raises(Exception) as exc_info:
        with mock.patch.object(sys, 'argv', run_args):
            args = parse_args(run_args)
            cmd_params = vars(args)
            check_run_args(cmd_params)
            assert exc_info.value == "Missing nodes option. You can either use --nodes-val or -nodes-distr"

    # Check if an exception is thrown when both --nodes-val and --nodes-distr are inserted
    run_args = [
        "adgen",
        "run",
        "--url", "bolt://localhost:7687",
        "--user", "run_user",
        "--passwd", "run_passwd",
        "--nodes-val", "400",
        "--nodes-distr", "uniform(100,300)",
        "--domain", "run_domain.local"
    ]

    with pytest.raises(Exception) as exc_info:
        with mock.patch.object(sys, 'argv', run_args):
            args = parse_args(run_args)
            cmd_params = vars(args)
            check_run_args(cmd_params)
            assert exc_info.value == "You cannot use both --nodes-val and --nodes-distr at the same time. You only have to use one of them"

    # Check if an exception is thrown when using --nodes-distr and inserting an invalid distribution
    invalid_distr = "invalid_distribution(100,300)"
    run_args = [
        "adgen",
        "run",
        "--url", "bolt://localhost:7687",
        "--user", "run_user",
        "--passwd", "run_passwd",
        "--nodes-distr", invalid_distr,
        "--domain", "run_domain.local"
    ]

    with pytest.raises(Exception) as exc_info:
        with mock.patch.object(sys, 'argv', run_args):
            args = parse_args(run_args)
            cmd_params = vars(args)
            check_run_args(cmd_params)
            assert exc_info.value == f"Distribution {invalid_distr} does not exist. Choose from:" \
                                     f"\n\t- uniform(a,b)" \
                                     f"\n\t- triangular(low,high)" \
                                     f"\n\t- gauss(mu,sigma)" \
                                     f"\n\t- normal(mu,sigma)"


def test_run_mode():
    """Test the correct behavior of the run mode"""
    domain_name = "run_domain.local"

    run_args = [
        "adgen",
        "run",
        "--url", "bolt://localhost:7687",
        "--user", "neo4j",
        "--passwd", "neo4jpwd",
        "--nodes-distr", "uniform(200,300)",
        "--domain", domain_name
    ]

    with mock.patch.object(sys, 'argv', run_args):
        args = parse_args(run_args)
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

        run(cmd_params)

        domain = {}
        for res in session.run("MATCH (n:Domain) RETURN n.name"):
            domain.update(res)
        assert len(domain) == 1
        assert domain.get('n.name') == domain_name.upper()

        users = []
        for u in session.run("MATCH (n:User) RETURN n"):
            users.append(u)
        assert 200 <= len(users) <= 300
