#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid  : 67a8764c-9837-11ed-9f08-04cf4bfb0bc5
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2023-01-19
# -----------


"""
Methods defining the `docs` command.
"""

# ------------
# System Modules - Included with Python

from pathlib import Path

# ------------
# 3rd Party

import click

from rich.traceback import install

install(show_locals=False)

from rich.console import Console

console = Console()

# ------------
# Custom Modules

from .validate import validate

# from .repair import repair
# from .stats import stats
# from .graph import graph


@click.group()
@click.pass_context
def main(*args, **kwargs):
    """
    The `docs` command provides access to various tools to validate and
    alter the system.

    # Usage

    $ docs validate ./doc/root

    $ docs graph ./doc/root

    $ docs stats ./doc/root

    $ docs repair --dry-run links ./doc/root

    $ docs repair links ./doc/root

    $ docs repair --dry-run images ./doc/root

    $ docs repair images ./doc/root

    $ docs repair --dry-run headers ./doc/root

    $ docs repair --dry-run headers --list ./doc/root

    $ docs repair headers --list ./doc/root

    $ docs repair headers ./doc/root
    """

    # Initialize the shared context object to a dictionary and configure
    # it for the app
    ctx = args[0]
    ctx.ensure_object(dict)

    # ctx.obj["cfg"] = setup([Path(p) for p in kwargs["config"]])


# --------
# Commands

main.add_command(validate)
# main.add_command(stats)
# main.add_command(graph)
# main.add_command(repair)
