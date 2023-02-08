#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams

# uuid  : 740a4b68-9837-11ed-962f-04cf4bfb0bc5
# author: Troy Williams
# email : troy.williams@bluebill.net
# date  : 2023-01-19
# -----------

"""
`stats` provides an estimated word count across all of the markdown
files.

"""

# ------------
# System Modules - Included with Python

from pathlib import Path
from datetime import datetime

# ------------
# 3rd Party - From pip

import click

from rich.console import Console

console = Console()

# ------------
# Custom Modules

from .markdown import (
    MarkdownDocument,
    count_all_words,
    find_markdown_files,
)

# -------------


@click.command("stats")
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
def stats(*args, **kwargs):
    """
    Given the `root` path, recursively find all the Markdown files and
    estimate the total word count.

    ```
    Started  - 2021-05-19 13:57:30.698969
    Finished - 2021-05-19 13:57:49.755689
    Elapsed:   0:00:19.056720

    Total Documents:      735
    Total Words:      182,584
    Estimated Pages:    365.2
    ```

    # Usage

    $ docs stats ./doc/root

    """

    root_path = kwargs["root_path"].expanduser().resolve()

    console.print(f"Searching: {root_path}")

    if root_path.is_file():
        console.print("[red]Root path has to be a directory.[/red]")
        ctx.abort()

    search_start_time = datetime.now()

    markdown_files = find_markdown_files(root_path)

    # Get a total word and page count estimate
    word_count = count_all_words(markdown_files)

    # stop the clock
    search_end_time = datetime.now()

    # Convert the dict counts to strings and find the length so we can
    # use the value to format the numbers to line up properly f'{value:
    # {width}.{precision}}' Since this is for formatting and display, I
    # am not bothering with anything fancier

    width = max(
        len(str(len(markdown_files))),
        len(str(word_count.estimated_word_count)),
    )

    console.print()
    console.print(f"[cyan]Markdown Documents: {len(markdown_files):>{width}}[/cyan]")

    console.print(
        f"[cyan]Estimated Words:   {word_count.estimated_word_count:>{width},}[/cyan]"
    )
    console.print(
        f"[cyan]Estimated Pages:    {word_count.estimated_page_count:>{width},.1f}[/cyan]"
    )

    console.print()
    console.print(f"[cyan]Started:  {search_start_time}[/cyan]")
    console.print(f"[cyan]Finished: {search_end_time}[/cyan]")
    console.print(
        f"[cyan]Elapsed:              {search_end_time - search_start_time}[/cyan]"
    )
    console.print()
