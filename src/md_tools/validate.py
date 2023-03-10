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
    validate_markdown_relative_links,
    find_markdown_files,
    find_all_files,
    ValidationIssue,
)

# -------------


def print_doc(doc: MarkdownDocument) -> None:
    """
    Given a MarkdownDocument, display all the relative links to stdout
    along with the line numbers.
    """

    line_count = len(doc.contents)
    digits = len(str(line_count))

    for l in doc.all_relative_links:
        if len(l.matches) == 1:
            console.print(
                f"Line: {l.number:>{digits}} -> [yellow]{l.matches[0].full}[/yellow]"
            )

        else:
            console.print(f"Line: {l.number:{digits}} -> Links:{len(l.matches)}")

            for i, m in enumerate(l.matches):
                console.print(f"  - {i} Link -> [yellow]{m.full}[/yellow]")


def print_incorrect_line(incorrect: ValidationIssue) -> None:
    """
    Given the incorrect result, print it out to console along with the line number and the issue.
    """

    console.print(
        f"Line: {incorrect.line.number + 1}: -> [yellow]INCORRECT:[/yellow] [cyan]{incorrect.issue}[/cyan]"
    )


def print_missing_line(missing: ValidationIssue) -> None:
    console.print(
        f"Line: {missing.line.number + 1}: -> [red]MISSING:[/red] [cyan]{missing.issue}[/cyan]"
    )


def print_potential_asset_matches(
    incorrect: ValidationIssue, assets: dict[str, Path]
) -> None:
    """
    Given an incorrect result, print out all potential matching assets.
    """

    for asset in assets[incorrect.issue.name]:
        console.print(f"    [cyan]OPTIONS -> {asset} [/cyan]")


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
@click.option(
    "--repair",
    is_flag=True,
    help="Repair broken links. It will only repair links that are easy to fix (i.e. only one match in the system).",
)
def validate(*args, **kwargs):
    """
    Recursively find all Markdown files and build a look up structure so
    that all of the relative links (both hyperlinks and image links)
    can be validated. That is, the links should point to a file in the
    system (an image, a markdown or something else).

    # Usage

    $ docs validate ./doc/root

    $ docs validate /home/troy/repositories/documentation/aegis.documentation.sphinx/docs/source

    """

    ctx = args[0]

    root_path = kwargs["root_path"].expanduser().resolve()

    repair_links = kwargs["repair"] if "repair" in kwargs else False

    console.print(f"Searching: {root_path}")

    if root_path.is_file():
        console.print("[red]Root path has to be a directory.[/red]")
        ctx.abort()

    search_start_time = datetime.now()

    markdown_files: set[MarkdownDocument] = find_markdown_files(root_path)

    assets: dict[str, Path] = find_all_files(root_path)

    # ----
    # Validate Relative Links

    console.print("Validating Relative Markdown Links and Image Links...")
    console.print()

    issue_count = 0
    repaired_file_count = 0
    defective_file_count = 0

    for doc in markdown_files:
        repaired_links = False

        results = validate_markdown_relative_links(doc, assets, root_path)

        if "incorrect" in results or "missing" in results:
            console.print(
                f"[green]MARKDOWN: {doc.filename}[/green] Links: [yellow]{len(doc.contents)}[/yellow]"
            )
            console.print()

            defective_file_count += 1

            if "incorrect" in results:
                # The filename exists as an asset, just the paths don't
                # line up

                issue_count += len(results["incorrect"])

                if repair_links:
                    # ---
                    # Attempt to Repair Links

                    # If there is an incorrect result and there is only
                    # one asset that it could be, replace the asset set
                    # a flag so that the document contents are written
                    # to file. We'll need to set a flag to write the
                    # contents of the file after all repairs are made

                    for incorrect in results["incorrect"]:
                        if len(assets[incorrect.issue.name]) == 1:
                            asset = assets[incorrect.issue.name][0]

                            print_incorrect_line(incorrect)
                            console.print(f"[yellow]Replacing with: {asset} [/yellow]")

                            # f"Line: {incorrect.line.number + 1}: -> [yellow]INCORRECT:[/yellow] [cyan]{incorrect.issue}[/cyan]"

                            new_line = incorrect.line.line.replace(
                                str(incorrect.issue), str(asset)
                            )
                            doc.contents[incorrect.line.number] = new_line
                            repaired_links = True

                            console.print()

                        else:
                            print_incorrect_line(incorrect)
                            print_potential_asset_matches(incorrect, assets)
                            console.print(
                                "[red]Cannot Repair - too many choices! Manual intervention required.[/red]"
                            )
                            console.print()

                else:
                    for incorrect in results["incorrect"]:
                        print_incorrect_line(incorrect)
                        print_potential_asset_matches(incorrect, assets)
                        console.print()

            if "missing" in results:
                # filename doesn't exist within the asset dictionary.

                issue_count += len(results["missing"])

                for missing in results["missing"]:
                    print_missing_line(missing)

            if repair_links:
                doc.filename.write_text("\n".join(doc.contents))
                repaired_file_count += 1

                console.print(f"[green]Changes saved to `{doc.filename.name}`[/green]")

            console.print()

    # stop the clock
    search_end_time = datetime.now()

    # Convert the dict counts to strings and find the length so we can
    # use the value to format the numbers to line up properly f'{value:
    # {width}.{precision}}' Since this is for formatting and display, I
    # am not bothering with anything fancier

    width = max(
        len(str(len(markdown_files))),
        len(str(len(assets))),
    )

    console.print(f"[cyan]Documents Found:    {len(assets):>{width}}[/cyan]")
    console.print(f"[cyan]Markdown Documents: {len(markdown_files):>{width}}[/cyan]")

    if issue_count == 0:
        console.print(":+1: [green]No Issues Detected![/green]")
        console.print()

    if defective_file_count > 0:
        console.print(f"[red]Defective files: {defective_file_count}[/red]")
        console.print()

    if repaired_file_count > 0:
        console.print(f":+1: [green]Repaired {repaired_file_count} files[/green]")
        console.print()

    console.print()
    console.print(f"[cyan]Started:  {search_start_time}[/cyan]")
    console.print(f"[cyan]Finished: {search_end_time}[/cyan]")
    console.print(
        f"[cyan]Elapsed:              {search_end_time - search_start_time}[/cyan]"
    )
    console.print()
