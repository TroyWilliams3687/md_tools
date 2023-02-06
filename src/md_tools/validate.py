#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid  : 7872a312-9837-11ed-9b77-04cf4bfb0bc5
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2023-01-19
# -----------

"""
The `validate` command is used to analyze the Markdown files in the
system for issues. The `repair` command can fix some of the issues.
"""

# ------------
# System Modules - Included with Python

# from datetime import datetime
# from multiprocessing import Pool
# from functools import partial

from pathlib import Path
from itertools import chain
from datetime import datetime

# ------------
# 3rd Party - From pip

import click

from rich.console import Console

console = Console()

# ------------
# Custom Modules

from .markdown import MarkdownDocument, validate_markdown_relative_links


# from ..documentos.document_validation import (
#     validate_urls,
#     validate_images,
# )

# -------------


def print_doc(doc:MarkdownDocument) -> None:
    """
    Given a MarkdownDocument, display all the relative links to stdout
    along with the line numbers.
    """

    line_count = len(doc.contents)
    digits = len(str(line_count))

    for l in doc.all_relative_links:

        if len(l.matches) == 1:

            console.print(f"Line: {l.number:>{digits}} -> [yellow]{l.matches[0].full}[/yellow]")

        else:

            console.print(f"Line: {l.number:{digits}} -> Links:{len(l.matches)}")

            for i, m in enumerate(l.matches):
                console.print(f"  - {i} Link -> [yellow]{m.full}[/yellow]")



@click.command("validate")
@click.pass_context
@click.argument(
    "root_path",
    type=click.Path(
        exists=True,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
)
def validate(*args, **kwargs):
    """
    Perform validation checks for Markdown files and LST files.

    # Usage

    $ docs validate ./doc/root

    $ docs validate /home/troy/repositories/documentation/aegis.documentation.sphinx/docs/source

    """
    # config = args[0].obj["cfg"]

    # ------------
    # Build code that uses pathlib.path.rglob to recursively find all markdown files

    # inspect each file, line-by-line validating:
    # Image Check - Internal
    #   - Does the file exist at the URL?
    #   - Relative Image Check
    #   - Absolute Image Check
    # File Check
    #   - Does the local file exist?
    #   - Relative
    #   - Absolute
    # URL Check
    #   - Is the URL Valid and does it point to a valid Resource?
    #   - this can use aiohttp, a queue and asyncio to speed this up

    # should build a set of rules that can be run against each line of the markdown file
    # should be able to deal gracefully with code blocks or other blocks, i.e. YAML blocks

    # perhaps use my markdown object - it might be easier. The key is to write the file line number

    ctx = args[0]

    root_path = kwargs["root_path"].expanduser().resolve()

    console.print(f"Searching: {root_path}")

    if root_path.is_file():
        console.print("[red]Root path has to be a directory.[/red]")
        ctx.abort()

    # Store a reference to the Markdown files
    markdown_files:set[MarkdownDocument] = set()

    # ----
    # All files are considered assets, including the markdown files. The
    # assets are simply things that can be the target of a link. The
    # key will be the filename and the target a list of Path objects
    # representing files with the same name, but in different paths.

    # NOTE: When using the stored paths, they need to be relative to the
    # root folder

    assets:dict[str, Path] = {}

    search_start_time = datetime.now()

    for filename in root_path.rglob("*"):

        # console.print(f'[cyan]{filename}[/cyan]')

        # add the asset to the correct folder, making sure it is relative to the root folder
        assets.setdefault(filename.name, []).append(filename.relative_to(root_path))

        if filename.suffix == ".md":

            doc = MarkdownDocument(filename)
            markdown_files.add(doc)

            # print_doc(doc)
            # console.print()


    # Convert the dict counts to strings and find the length so we can
    # use the value to format the numbers to line up properly f'{value:
    # {width}.{precision}}' Since this is for formatting and display, I
    # am not bothering with anything fancier

    width = max(len(str(len(markdown_files))), len(str(len(assets))))

    console.print()
    console.print(f"Found:    {len(assets):>{width}}")
    console.print(f"Markdown: {len(markdown_files):>{width}}")
    console.print()

    # ----
    # Validate Relative Links

    console.print('Validating Relative Markdown Links and Image Links...')
    console.print()

    issue_count = 0

    for doc in markdown_files:

        results = validate_markdown_relative_links(doc, assets)

        if "incorrect" in results or "missing" in results:
            console.print(f"[green]MARKDOWN: {doc.filename}[/green] Links: [yellow]{len(doc.contents)}[/yellow]")
            console.print()

            if "incorrect" in results:
                # The filename exists as an asset, just the paths don't
                # line up

                issue_count += len(results["incorrect"])

                for incorrect in results["incorrect"]:

                    console.print(f"Line: {incorrect.line.number}: -> [yellow]INCORRECT:[/yellow] [cyan]{incorrect.issue}[/cyan]")

                    for asset in assets[incorrect.issue.name]:
                        console.print(f"    [cyan]OPTIONS -> {asset} [/cyan]")

                    console.print()

            if "missing" in results:
                # filename doesn't exist within the asset dictionary.

                issue_count += len(results["missing"])

                for missing in results["missing"]:

                    console.print(f"Line: {missing.line.number}: -> [red]MISSING:[/red] [cyan]{missing.issue}[/cyan]")

            console.print()

    if issue_count == 0:
        console.print(":+1: [green]No Issues Detected![/green]")
        console.print()

    search_end_time = datetime.now()

    # console.print()
    # console.print('----')
    console.print(f"[cyan]Started:   {search_start_time}[/cyan]")
    console.print(f"[cyan]Finished:  {search_end_time}[/cyan]")
    console.print(f"[cyan]Elapsed:   {search_end_time - search_start_time}[/cyan]")
    console.print()
